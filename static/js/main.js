// 主要的JavaScript功能

$(document).ready(function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerList);
    });
    
    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 添加页面加载动画
    $('.card').addClass('fade-in-up');
    
    // 搜索功能增强
    setupSearchEnhancement();
    
    // 评分功能
    setupRatingSystem();
    
    // 用户行为跟踪
    setupBehaviorTracking();
});

// 搜索功能增强
function setupSearchEnhancement() {
    let searchTimeout;
    
    $('input[name="search"]').on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val();
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(function() {
                performSearch(query);
            }, 500);
        }
    });
}

// 执行搜索
function performSearch(query) {
    $.get('/api/search_books', { q: query, page: 1 })
        .done(function(data) {
            if (data.success) {
                displaySearchResults(data.books);
            }
        })
        .fail(function() {
            console.log('搜索失败');
        });
}

// 显示搜索结果
function displaySearchResults(books) {
    // 这里可以实现实时搜索结果显示
    console.log('搜索结果:', books);
}

// 评分系统
function setupRatingSystem() {
    $('.rating-stars').on('click', '.star', function() {
        const rating = $(this).data('rating');
        const bookId = $(this).closest('.rating-container').data('book-id');
        
        // 更新星星显示
        updateStars($(this).closest('.rating-stars'), rating);
        
        // 提交评分
        submitRating(bookId, rating);
    });
    
    $('.rating-stars').on('mouseenter', '.star', function() {
        const rating = $(this).data('rating');
        updateStars($(this).closest('.rating-stars'), rating, true);
    });
    
    $('.rating-stars').on('mouseleave', function() {
        const currentRating = $(this).data('current-rating') || 0;
        updateStars($(this), currentRating, false);
    });
}

// 更新星星显示
function updateStars(container, rating, isHover = false) {
    container.find('.star').each(function(index) {
        const starIndex = index + 1;
        if (starIndex <= rating) {
            $(this).removeClass('far').addClass('fas');
        } else {
            $(this).removeClass('fas').addClass('far');
        }
    });
    
    if (!isHover) {
        container.data('current-rating', rating);
    }
}

// 提交评分
function submitRating(bookId, rating) {
    $.ajax({
        url: '/api/rate_book',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            book_id: bookId,
            rating: rating,
            review: ''
        }),
        success: function(data) {
            if (data.success) {
                showNotification('评分提交成功！', 'success');
            } else {
                showNotification('评分提交失败：' + data.error, 'error');
            }
        },
        error: function() {
            showNotification('评分提交失败，请稍后再试。', 'error');
        }
    });
}

// 用户行为跟踪
function setupBehaviorTracking() {
    // 记录页面浏览时间
    let startTime = Date.now();
    
    $(window).on('beforeunload', function() {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        recordBehavior('view', duration);
    });
    
    // 记录点击行为
    $('.book-card').on('click', function() {
        const bookId = $(this).data('book-id');
        recordBehavior('view', 0, bookId);
    });
    
    // 记录搜索行为
    $('form[action*="books"]').on('submit', function() {
        const searchQuery = $(this).find('input[name="search"]').val();
        if (searchQuery) {
            recordBehavior('search', 0, null, searchQuery);
        }
    });
}

// 记录用户行为
function recordBehavior(behaviorType, duration = 0, bookId = null, extraData = null) {
    if (!window.currentUserId) return;
    
    $.ajax({
        url: '/api/user_behavior',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            book_id: bookId || 0,
            behavior_type: behaviorType,
            duration: duration,
            extra_data: extraData
        }),
        success: function(data) {
            if (data.success) {
                console.log('行为记录成功');
            }
        },
        error: function() {
            console.log('行为记录失败');
        }
    });
}

// 显示通知
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 在页面顶部显示通知
    $('main').prepend(alertHtml);
    
    // 自动隐藏通知
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
}

// 借阅图书
function borrowBook(bookId) {
    if (!confirm('确定要借阅这本书吗？')) {
        return;
    }
    
    $.ajax({
        url: '/api/borrow_book',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ book_id: bookId }),
        success: function(data) {
            if (data.success) {
                showNotification('借阅成功！', 'success');
                setTimeout(function() {
                    location.reload();
                }, 1500);
            } else {
                showNotification('借阅失败：' + data.error, 'error');
            }
        },
        error: function() {
            showNotification('借阅失败，请稍后再试。', 'error');
        }
    });
}

// 归还图书
function returnBook(borrowingId) {
    if (!confirm('确定要归还这本书吗？')) {
        return;
    }
    
    $.ajax({
        url: '/api/return_book',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ borrowing_id: borrowingId }),
        success: function(data) {
            if (data.success) {
                showNotification('归还成功！', 'success');
                setTimeout(function() {
                    location.reload();
                }, 1500);
            } else {
                showNotification('归还失败：' + data.error, 'error');
            }
        },
        error: function() {
            showNotification('归还失败，请稍后再试。', 'error');
        }
    });
}

// 加载推荐
function loadRecommendations() {
    $('#recommendations-container').html(`
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-2">正在为您生成个性化推荐...</p>
        </div>
    `);
    
    $.get('/api/recommendations')
        .done(function(data) {
            if (data.success) {
                displayRecommendations(data.recommendations);
            } else {
                $('#recommendations-container').html(`
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        暂时无法生成推荐，请稍后再试。
                    </div>
                `);
            }
        })
        .fail(function() {
            $('#recommendations-container').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle me-2"></i>
                    加载推荐失败，请检查网络连接。
                </div>
            `);
        });
}

// 显示推荐
function displayRecommendations(recommendations) {
    if (recommendations.length === 0) {
        $('#recommendations-container').html(`
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                暂无推荐，请先借阅一些图书或进行评分。
            </div>
        `);
        return;
    }
    
    let html = '<div class="row">';
    recommendations.forEach(function(book) {
        html += `
            <div class="col-md-3 col-sm-6 mb-4">
                <div class="card h-100 book-card" data-book-id="${book.id}">
                    <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                        <i class="fas fa-book fa-3x text-muted"></i>
                    </div>
                    <div class="card-body">
                        <h6 class="card-title text-truncate">${book.title}</h6>
                        <p class="card-text text-muted small">${book.author}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-secondary">${book.category}</span>
                            <small class="text-muted">${book.publish_year}</small>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <a href="/book/${book.id}" class="btn btn-sm btn-primary w-100">
                            查看详情
                        </a>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    $('#recommendations-container').html(html);
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// 格式化时间
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 本地存储工具
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('存储失败:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('读取失败:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('删除失败:', e);
        }
    }
};

// 导出全局函数
window.borrowBook = borrowBook;
window.returnBook = returnBook;
window.loadRecommendations = loadRecommendations;
window.showNotification = showNotification;