// 主要的JavaScript功能

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 添加页面加载动画
    addPageLoadAnimation();
    
    // 初始化搜索功能
    initSearchFunctionality();
    
    // 初始化评分功能
    initRatingFunctionality();
    
    // 初始化推荐系统
    initRecommendationSystem();
});

// 页面加载动画
function addPageLoadAnimation() {
    const cards = document.querySelectorAll('.book-card, .feature-card, .card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// 搜索功能
function initSearchFunctionality() {
    const searchInput = document.getElementById('search');
    if (searchInput) {
        // 实时搜索建议
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                // 这里可以添加AJAX请求来获取搜索建议
                console.log('搜索查询:', query);
            }
        });
        
        // 搜索历史
        const searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        if (searchHistory.length > 0) {
            // 可以在这里显示搜索历史
        }
    }
}

// 评分功能
function initRatingFunctionality() {
    const ratingInputs = document.querySelectorAll('.rating-input input');
    const starLabels = document.querySelectorAll('.star-label');
    
    ratingInputs.forEach((input, index) => {
        input.addEventListener('change', function() {
            const rating = this.value;
            console.log('用户评分:', rating);
            
            // 更新星星显示
            starLabels.forEach((label, labelIndex) => {
                const icon = label.querySelector('i');
                if (labelIndex < rating) {
                    icon.className = 'fas fa-star';
                } else {
                    icon.className = 'far fa-star';
                }
            });
        });
    });
}

// 推荐系统功能
function initRecommendationSystem() {
    // 获取推荐数据
    const recommendationButtons = document.querySelectorAll('[data-recommendation-type]');
    
    recommendationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const type = this.dataset.recommendationType;
            loadRecommendations(type);
        });
    });
}

// 加载推荐
function loadRecommendations(type) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;
    
    // 显示加载状态
    container.innerHTML = '<div class="text-center"><div class="loading"></div><p>加载推荐中...</p></div>';
    
    // 模拟AJAX请求
    setTimeout(() => {
        // 这里应该是实际的AJAX请求
        console.log('加载推荐类型:', type);
        
        // 模拟推荐数据
        const recommendations = [
            { title: '推荐图书1', author: '作者1', category: '计算机科学' },
            { title: '推荐图书2', author: '作者2', category: '文学' },
            { title: '推荐图书3', author: '作者3', category: '历史' }
        ];
        
        displayRecommendations(recommendations);
    }, 1000);
}

// 显示推荐
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;
    
    let html = '<div class="row">';
    recommendations.forEach(book => {
        html += `
            <div class="col-md-4 mb-3">
                <div class="card book-card">
                    <div class="card-body">
                        <h6 class="card-title">${book.title}</h6>
                        <p class="card-text text-muted">${book.author}</p>
                        <span class="badge bg-secondary">${book.category}</span>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// 借阅功能
function borrowBook(bookId) {
    if (!confirm('确定要借阅这本书吗？')) {
        return;
    }
    
    // 这里应该发送AJAX请求到后端
    console.log('借阅图书ID:', bookId);
    
    // 模拟成功
    showNotification('借阅成功！', 'success');
}

// 归还功能
function returnBook(borrowingId) {
    if (!confirm('确定要归还这本书吗？')) {
        return;
    }
    
    // 这里应该发送AJAX请求到后端
    console.log('归还借阅ID:', borrowingId);
    
    // 模拟成功
    showNotification('归还成功！', 'success');
}

// 显示通知
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // 自动消失
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// 用户行为跟踪
function trackUserBehavior(action, data) {
    // 这里可以发送用户行为数据到后端
    console.log('用户行为:', action, data);
    
    // 存储到本地存储
    const behaviors = JSON.parse(localStorage.getItem('userBehaviors') || '[]');
    behaviors.push({
        action: action,
        data: data,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('userBehaviors', JSON.stringify(behaviors.slice(-50))); // 只保留最近50条
}

// 图书浏览行为
function trackBookView(bookId, bookTitle) {
    trackUserBehavior('view_book', {
        bookId: bookId,
        bookTitle: bookTitle
    });
}

// 搜索行为
function trackSearch(query) {
    trackUserBehavior('search', {
        query: query
    });
}

// 借阅行为
function trackBorrow(bookId, bookTitle) {
    trackUserBehavior('borrow_book', {
        bookId: bookId,
        bookTitle: bookTitle
    });
}

// 评分行为
function trackRating(bookId, rating) {
    trackUserBehavior('rate_book', {
        bookId: bookId,
        rating: rating
    });
}

// 响应式导航栏
function initResponsiveNavbar() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // 点击导航链接时自动收起
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
    }
}

// 初始化响应式导航栏
document.addEventListener('DOMContentLoaded', function() {
    initResponsiveNavbar();
});

// 平滑滚动
function smoothScrollTo(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 返回顶部功能
function initBackToTop() {
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'btn btn-primary position-fixed';
    backToTopButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;';
    
    document.body.appendChild(backToTopButton);
    
    // 滚动时显示/隐藏按钮
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    // 点击返回顶部
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 初始化返回顶部功能
document.addEventListener('DOMContentLoaded', function() {
    initBackToTop();
});

// 导出函数供其他模块使用
window.LibraryApp = {
    trackUserBehavior,
    trackBookView,
    trackSearch,
    trackBorrow,
    trackRating,
    showNotification,
    smoothScrollTo
};