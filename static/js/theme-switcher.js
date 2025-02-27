// static/js/theme-switcher.js
document.addEventListener('DOMContentLoaded', function() {
    // 获取当前主题设置
    const currentTheme = localStorage.getItem('theme') || 'light';

    // 在文档加载时应用保存的主题
    document.documentElement.setAttribute('data-bs-theme', currentTheme);

    // 更新主题切换按钮状态
    updateThemeToggle(currentTheme);

    // 监听主题切换按钮点击事件
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // 获取当前主题
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            // 切换主题
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            // 应用新主题
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            // 保存主题设置
            localStorage.setItem('theme', newTheme);

            // 更新按钮状态
            updateThemeToggle(newTheme);
        });
    }
});

// 更新主题切换按钮状态
function updateThemeToggle(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    if (themeToggle && themeIcon) {
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-moon');
            themeIcon.classList.add('bi-sun');
            themeToggle.setAttribute('title', '切换到亮色模式');
        } else {
            themeIcon.classList.remove('bi-sun');
            themeIcon.classList.add('bi-moon');
            themeToggle.setAttribute('title', '切换到暗色模式');
        }
    }
}