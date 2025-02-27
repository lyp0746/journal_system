// static/js/form-enhancements.js
document.addEventListener('DOMContentLoaded', function() {
    // 自动显示表单验证错误
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        if (input.classList.contains('is-invalid')) {
            input.addEventListener('focus', function() {
                // 获取相关的反馈元素
                const feedback = input.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.style.display = 'block';
                }
            });
        }
    });

    // 文件输入增强
    document.querySelectorAll('.custom-file-input').forEach(fileInput => {
        // 监听文件选择变化
        fileInput.addEventListener('change', function() {
            // 获取文件名显示元素
            const fileLabel = fileInput.nextElementSibling;
            if (fileLabel && fileInput.files.length > 0) {
                // 显示选择的文件名
                fileLabel.textContent = fileInput.files[0].name;
            }
        });
    });

    // 表单提交按钮加载状态
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton && !submitButton.classList.contains('no-loading')) {
                // 禁用按钮并显示加载状态
                submitButton.disabled = true;

                // 保存原始文本
                const originalText = submitButton.innerHTML;

                // 设置加载状态
                submitButton.innerHTML = `  
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>  
                    处理中...  
                `;

                // 防止表单多次提交
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 10000); // 10秒超时保护
            }
        });
    });

    // 日期选择器增强
    if (typeof flatpickr !== 'undefined') {
        flatpickr(".datepicker", {
            locale: "zh",
            dateFormat: "Y-m-d",
            allowInput: true
        });
    }

    // 选择框增强
    if (typeof Choices !== 'undefined') {
        document.querySelectorAll('.choices-select').forEach(select => {
            new Choices(select, {
                searchEnabled: true,
                itemSelectText: '',
                shouldSort: false,
                placeholder: true,
                placeholderValue: '请选择...'
            });
        });
    }
});