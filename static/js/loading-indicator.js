// static/js/loading-indicator.js
document.addEventListener('DOMContentLoaded', function() {
    // 创建加载指示器元素
    const loadingIndicator = document.createElement('div');
    loadingIndicator.classList.add('page-loading-indicator');
    loadingIndicator.innerHTML = `  
        <div class="spinner-border text-primary" role="status">  
            <span class="visually-hidden">加载中...</span>  
        </div>  
    `;
    document.body.appendChild(loadingIndicator);

    // 隐藏初始加载指示器
    loadingIndicator.style.display = 'none';

    // 全局页面加载指示器
    window.addEventListener('beforeunload', function() {
        loadingIndicator.style.display = 'flex';
    });

    // AJAX请求加载指示器
    const originalFetch = window.fetch;
    let activeRequests = 0;

    window.fetch = function() {
        // 显示加载指示器
        activeRequests++;
        if (activeRequests === 1) {
            loadingIndicator.style.display = 'flex';
        }

        return originalFetch.apply(this, arguments)
            .then(response => {
                // 隐藏加载指示器
                activeRequests--;
                if (activeRequests === 0) {
                    loadingIndicator.style.display = 'none';
                }
                return response;
            })
            .catch(error => {
                // 出错时也隐藏加载指示器
                activeRequests--;
                if (activeRequests === 0) {
                    loadingIndicator.style.display = 'none';
                }
                throw error;
            });
    };

    // 页面加载完成后隐藏初始加载指示器
    window.addEventListener('load', function() {
        // 短暂延迟以确保所有内容已渲染
        setTimeout(() => {
            document.body.classList.add('page-loaded');
        }, 100);
    });
});