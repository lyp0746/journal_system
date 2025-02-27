// static/js/mobile-enhancements.js
document.addEventListener('DOMContentLoaded', function() {
    // 检测是否是移动设备
    const isMobile = window.innerWidth < 768;

    if (isMobile) {
        // 添加边栏切换功能
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            // 创建侧边栏背景遮罩
            const backdrop = document.createElement('div');
            backdrop.classList.add('sidebar-backdrop');
            document.body.appendChild(backdrop);

            // 创建切换按钮
            const toggleBtn = document.createElement('button');
            toggleBtn.classList.add('btn', 'btn-primary', 'd-md-none', 'mobile-fab');
            toggleBtn.innerHTML = '<i class="bi bi-list"></i>';
            document.body.appendChild(toggleBtn);

            // 添加切换事件
            toggleBtn.addEventListener('click', function() {
                sidebar.classList.add('show');
                backdrop.classList.add('show');
            });

            // 点击背景关闭侧边栏
            backdrop.addEventListener('click', function() {
                sidebar.classList.remove('show');
                backdrop.classList.remove('show');
            });
        }

        // 添加返回顶部按钮
        const scrollThreshold = 300;
        const backToTopBtn = document.createElement('button');
        backToTopBtn.classList.add('btn', 'btn-secondary', 'mobile-fab');
        backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        backToTopBtn.style.bottom = '86px'; // 位置在侧边栏按钮上方
        backToTopBtn.style.display = 'none';
        document.body.appendChild(backToTopBtn);

        // 监听滚动事件
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > scrollThreshold) {
                backToTopBtn.style.display = 'flex';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });

        // 返回顶部事件
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // 优化表格显示
        document.querySelectorAll('table:not(.no-responsive)').forEach(table => {
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.classList.add('table-responsive');
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }
});