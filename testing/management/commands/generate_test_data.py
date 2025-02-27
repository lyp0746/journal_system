# testing/management/commands/generate_test_data.py
from django.core.management.base import BaseCommand
import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from faker import Faker

from submission.models import Paper, Keyword
from review.models import Review, Decision

User = get_user_model()
fake = Faker('zh_CN')


class Command(BaseCommand):
    help = '为测试用户生成测试数据'

    def add_arguments(self, parser):
        parser.add_argument('--authors', type=int, default=5, help='生成的测试作者数量')
        parser.add_argument('--papers', type=int, default=20, help='生成的测试稿件数量')
        parser.add_argument('--reviewers', type=int, default=10, help='生成的测试审稿人数量')
        parser.add_argument('--reviews', type=int, default=30, help='生成的测试审稿意见数量')

    def handle(self, *args, **options):
        author_count = options['authors']
        paper_count = options['papers']
        reviewer_count = options['reviewers']
        review_count = options['reviews']

        self.stdout.write('开始生成测试数据...')

        # 清理现有的测试数据
        self.clean_test_data()

        # 创建测试作者
        test_authors = self.create_test_authors(author_count)
        self.stdout.write(f'已创建 {len(test_authors)} 个测试作者')

        # 创建测试审稿人
        test_reviewers = self.create_test_reviewers(reviewer_count)
        self.stdout.write(f'已创建 {len(test_reviewers)} 个测试审稿人')

        # 创建测试编辑
        test_editors = self.create_test_editors(2)
        self.stdout.write(f'已创建 {len(test_editors)} 个测试编辑')

        # 创建测试稿件
        test_papers = self.create_test_papers(paper_count, test_authors, test_editors)
        self.stdout.write(f'已创建 {len(test_papers)} 个测试稿件')

        # 创建测试审稿
        test_reviews = self.create_test_reviews(review_count, test_papers, test_reviewers)
        self.stdout.write(f'已创建 {len(test_reviews)} 个测试审稿意见')

        self.stdout.write(self.style.SUCCESS('测试数据生成完成!'))

    def clean_test_data(self):
        """清理现有的测试数据"""
        # 删除标记为测试数据的内容
        Review.objects.filter(is_test_data=True).delete()
        Paper.objects.filter(is_test_data=True).delete()
        # 不删除用户，因为可能有关联的测试会话

    def create_test_authors(self, count):
        """创建测试作者"""
        authors = []
        for i in range(count):
            username = f"test_author_{i + 1}"
            email = f"{username}@test.example.com"

            # 检查用户是否已存在
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': 'AUTHOR',
                    'is_staff': False,
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()

            authors.append(user)

        return authors

    def create_test_reviewers(self, count):
        """创建测试审稿人"""
        reviewers = []
        for i in range(count):
            username = f"test_reviewer_{i + 1}"
            email = f"{username}@test.example.com"

            # 检查用户是否已存在
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': 'REVIEWER',
                    'is_staff': False,
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()

            reviewers.append(user)

        return reviewers

    def create_test_editors(self, count):
        """创建测试编辑"""
        editors = []
        for i in range(count):
            username = f"test_editor_{i + 1}"
            email = f"{username}@test.example.com"

            # 检查用户是否已存在
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': 'EDITOR',
                    'is_staff': True,
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()

            editors.append(user)

        return editors

    def create_test_papers(self, count, authors, editors):
        """创建测试稿件"""
        papers = []

        # 创建一些测试关键词
        keywords = []
        for _ in range(20):
            keyword, _ = Keyword.objects.get_or_create(name=fake.word())
            keywords.append(keyword)

        for i in range(count):
            # 随机选择作者和编辑
            author = random.choice(authors)
            editor = random.choice(editors) if editors and random.random() > 0.3 else None

            # 随机创建日期
            created_days_ago = random.randint(1, 60)
            created_date = timezone.now() - timedelta(days=created_days_ago)

            # 随机状态
            status_choices = ['SUBMITTED', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED', 'REVISIONS_REQUIRED']
            status_weights = [0.2, 0.3, 0.15, 0.15, 0.2]
            status = random.choices(status_choices, weights=status_weights)[0]

            # 创建稿件
            paper = Paper.objects.create(
                title=fake.sentence(),
                abstract=fake.paragraph(nb_sentences=5),
                author=author,
                editor=editor,
                status=status,
                is_test_data=True,
                created_at=created_date,
                updated_at=created_date + timedelta(
                    days=random.randint(1, 10)) if random.random() > 0.5 else created_date
            )

            # 添加关键词
            paper_keywords = random.sample(keywords, random.randint(3, 6))
            paper.keywords.set(paper_keywords)

            papers.append(paper)

        return papers

    def create_test_reviews(self, count, papers, reviewers):
        """创建测试审稿意见"""
        reviews = []

        for i in range(count):
            # 只为审稿中或已审稿的稿件添加审稿
            eligible_papers = [p for p in papers if
                               p.status in ['UNDER_REVIEW', 'ACCEPTED', 'REJECTED', 'REVISIONS_REQUIRED']]

            if not eligible_papers:
                continue

            paper = random.choice(eligible_papers)
            reviewer = random.choice(reviewers)

            # 随机分配状态
            status_choices = ['PENDING', 'COMPLETED']
            status_weights = [0.3, 0.7]
            status = random.choices(status_choices, weights=status_weights)[0]

            # 随机创建日期
            created_days_ago = random.randint(1, 30)
            created_date = timezone.now() - timedelta(days=created_days_ago)

            # 如果审稿已完成，添加评分和评语
            if status == 'COMPLETED':
                # 随机评分
                recommendation = random.choice(['ACCEPT', 'MINOR_REVISIONS', 'MAJOR_REVISIONS', 'REJECT'])
                comments = fake.paragraph(nb_sentences=random.randint(3, 8))
                completed_date = created_date + timedelta(days=random.randint(1, 14))
            else:
                recommendation = None
                comments = None
                completed_date = None

                # 创建审稿
            review = Review.objects.create(
                paper=paper,
                reviewer=reviewer,
                status=status,
                recommendation=recommendation,
                comments=comments,
                is_test_data=True,
                created_at=created_date,
                completed_at=completed_date
            )

            reviews.append(review)

        return reviews