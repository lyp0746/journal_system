// static/js/user-guide.js
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否需要显示新用户引导
    const showGuide = localStorage.getItem('userGuideShown') !== 'true';
    const userType = document.body.dataset.userType || '';

    // 针对不同角色的引导步骤
    const guideSteps = {
        'AUTHOR': [
            {
                element: '#sidebar-submissions',
                title: '我的投稿',
                content: '在这里可以查看您提交的所有稿件',
                position: 'right'
            },
            {
                element: '#new-submission-btn',
                title: '新稿件投递',
                content: '点击此按钮开始新的投稿流程',
                position: 'bottom'
            },
            {
                element: '#notification-dropdown',
                title: '通知中心',
                content: '您可以在这里查看所有系统通知',
                position: 'bottom'
            },
            {
                element: '#theme-toggle',
                title: '主题切换',
                content: '可以在亮色和暗色模式之间切换',
                position: 'bottom'
            }
        ],
        'REVIEWER': [
            {
                element: '#sidebar-reviews',
                title: '我的审稿任务',
                content: '在这里可以查看分配给您的所有审稿任务',
                position: 'right'
            },
            {
                element: '#notification-dropdown',
                title: '通知中心',
                content: '您可以在这里查看所有系统通知，包括新的审稿邀请',
                position: 'bottom'
            }
        ],
        'EDITOR': [
            {
                element: '#sidebar-dashboard',
                title: '编辑仪表板',
                content: '提供稿件处理概览',
                position: 'right'
            },
            {
                element: '#sidebar-submissions',
                title: '稿件管理',
                content: '管理所有投递的稿件',
                position: 'right'
            },
            {
                element: '#sidebar-statistics',
                title: '统计报表',
                content: '查看系统数据统计和分析',
                position: 'right'
            }
        ]
    };

    // 如果是新用户且有对应角色的引导步骤，显示引导
    if (showGuide && userType && guideSteps[userType]) {
        // 如果Shepherd.js存在，初始化引导
        if (typeof Shepherd !== 'undefined') {
            const tour = new Shepherd.Tour({
                useModalOverlay: true,
                defaultStepOptions: {
                    cancelIcon: {
                        enabled: true
                    },
                    classes: 'shepherd-theme-custom',
                    scrollTo: { behavior: 'smooth', block: 'center' }
                },
                exitOnEsc: true
            });

            // 添加角色对应的引导步骤
            guideSteps[userType].forEach(step => {
                tour.addStep({
                    id: step.element,
                    title: step.title,
                    text: step.content,
                    attachTo: {
                        element: step.element,
                        on: step.position
                    },
                    buttons: [
                        {
                            action: tour.next,
                            text: '下一步'
                        }
                    ]
                });
            });

            // 添加最后一个步骤
            tour.addStep({
                id: 'final-step',
                title: '开始使用',
                text: '引导结束，您现在可以开始使用系统了。如需再次查看引导，可在个人设置中重新打开。',
                buttons: [
                    {
                        action() {
                            // 记录引导已显示
                            localStorage.setItem('userGuideShown', 'true');
                            this.complete();
                        },
                        text: '完成'
                    }
                ]
            });

            // 启动引导
            tour.start();
        }
    }

    // 添加重置引导的按钮事件
    const resetGuideBtn = document.getElementById('reset-guide-btn');
    if (resetGuideBtn) {
        resetGuideBtn.addEventListener('click', function() {
            localStorage.removeItem('userGuideShown');
            alert('引导已重置，下次刷新页面时将再次显示引导。');
        });
    }
});