class LibraryRecommendationApp {
    constructor() {
        this.currentUser = null;
        this.loadingModal = null;
        this.toast = null;
        this.init();
    }

    async init() {
        // 初始化Bootstrap组件
        this.loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        this.toast = new bootstrap.Toast(document.getElementById('toast'));

        // 绑定事件监听器
        this.bindEventListeners();

        // 加载初始数据
        await this.loadInitialData();
    }

    bindEventListeners() {
        // 获取推荐按钮
        document.getElementById('getRecommendationsBtn').addEventListener('click', () => {
            this.getRecommendations();
        });

        // 用户行为分析按钮
        document.getElementById('getUserBehaviorBtn').addEventListener('click', () => {
            this.getUserBehavior();
        });

        // 评分按钮
        document.getElementById('rateBookBtn').addEventListener('click', () => {
            this.rateBook();
        });

        // 借阅按钮
        document.getElementById('borrowBookBtn').addEventListener('click', () => {
            this.borrowBook();
        });

        // 用户选择变化
        document.getElementById('userSelect').addEventListener('change', (e) => {
            this.currentUser = e.target.value;
        });
    }

    async loadInitialData() {
        try {
            this.showLoading();

            // 并行加载数据
            const [usersResponse, booksResponse, statsResponse] = await Promise.all([
                fetch('/api/users'),
                fetch('/api/books'),
                fetch('/api/stats')
            ]);

            const users = await usersResponse.json();
            const books = await booksResponse.json();
            const stats = await statsResponse.json();

            // 填充用户选择框
            this.populateUserSelect(users.users);

            // 填充图书选择框
            this.populateBookSelect(books.books);

            // 显示系统统计
            this.displaySystemStats(stats);

        } catch (error) {
            this.showToast('加载数据失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    populateUserSelect(users) {
        const select = document.getElementById('userSelect');
        select.innerHTML = '<option value="">请选择用户...</option>';

        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.user_id;
            option.textContent = `${user.name} (${user.profile}, ${user.age}岁)`;
            select.appendChild(option);
        });
    }

    populateBookSelect(books) {
        const select = document.getElementById('bookSelect');
        select.innerHTML = '<option value="">请选择图书...</option>';

        books.forEach(book => {
            const option = document.createElement('option');
            option.value = book.book_id;
            option.textContent = `${book.title} - ${book.author}`;
            select.appendChild(option);
        });
    }

    displaySystemStats(stats) {
        const statsContainer = document.getElementById('systemStats');
        statsContainer.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">用户总数:</span>
                <span class="stat-value">${stats.total_users}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">图书总数:</span>
                <span class="stat-value">${stats.total_books}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">评分总数:</span>
                <span class="stat-value">${stats.total_ratings}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">借阅总数:</span>
                <span class="stat-value">${stats.total_borrowings}</span>
            </div>
        `;
    }

    async getRecommendations() {
        if (!this.currentUser) {
            this.showToast('请先选择用户', 'warning');
            return;
        }

        try {
            this.showLoading();

            const method = document.getElementById('recommendMethod').value;
            const response = await fetch(`/api/user/${this.currentUser}/recommendations?method=${method}&num=10`);
            const data = await response.json();

            if (response.ok) {
                this.displayRecommendations(data);
                this.showToast('推荐获取成功', 'success');
            } else {
                throw new Error(data.error || '获取推荐失败');
            }

        } catch (error) {
            this.showToast('获取推荐失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayRecommendations(data) {
        const container = document.getElementById('recommendationsList');
        const methodBadge = document.getElementById('recommendationMethod');

        // 显示推荐方法
        const methodLabels = {
            'hybrid': '混合推荐',
            'collaborative': '协同过滤',
            'content': '内容过滤',
            'popularity': '流行度推荐'
        };
        methodBadge.textContent = methodLabels[data.method] || data.method;

        // 清空现有内容
        container.innerHTML = '';

        if (data.recommendations.length === 0) {
            container.innerHTML = '<div class="col-12 text-center text-muted">暂无推荐结果</div>';
        } else {
            data.recommendations.forEach(book => {
                const bookCard = this.createBookCard(book);
                container.appendChild(bookCard);
            });
        }

        // 显示推荐区域
        document.getElementById('recommendations').style.display = 'block';
        document.getElementById('recommendations').scrollIntoView({ behavior: 'smooth' });
    }

    createBookCard(book) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-3';

        col.innerHTML = `
            <div class="card book-card h-100 fade-in">
                <div class="card-body position-relative">
                    <div class="score-badge">${book.score}</div>
                    <h6 class="book-title">${book.title}</h6>
                    <p class="book-author">${book.author}</p>
                    <span class="book-category category-${book.category}">${book.category}</span>
                    <p class="card-text mt-2 text-muted small">${book.description.substring(0, 100)}...</p>
                    <div class="mt-auto">
                        <small class="text-muted">推荐方式: ${book.method}</small>
                    </div>
                </div>
            </div>
        `;

        return col;
    }

    async getUserBehavior() {
        if (!this.currentUser) {
            this.showToast('请先选择用户', 'warning');
            return;
        }

        try {
            this.showLoading();

            const response = await fetch(`/api/user/${this.currentUser}/behavior`);
            const data = await response.json();

            if (response.ok) {
                this.displayBehaviorAnalysis(data);
                this.showToast('行为分析获取成功', 'success');
            } else {
                throw new Error(data.error || '获取行为分析失败');
            }

        } catch (error) {
            this.showToast('获取行为分析失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayBehaviorAnalysis(data) {
        const container = document.getElementById('behaviorAnalysis');
        const analysis = data.behavior_analysis;

        if (analysis.error) {
            container.innerHTML = `<div class="alert alert-warning">${analysis.error}</div>`;
            return;
        }

        let html = '';

        // 用户基本信息
        html += `
            <div class="analysis-section">
                <div class="analysis-title">
                    <i class="fas fa-user me-2"></i>用户信息
                </div>
                <div class="stat-item">
                    <span class="stat-label">姓名:</span>
                    <span class="stat-value">${analysis.user_info.name}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">类型:</span>
                    <span class="stat-value">${analysis.user_info.profile}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">年龄:</span>
                    <span class="stat-value">${analysis.user_info.age}岁</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">兴趣:</span>
                    <span class="stat-value">${analysis.user_info.interests}</span>
                </div>
            </div>
        `;

        // 阅读统计
        html += `
            <div class="analysis-section">
                <div class="analysis-title">
                    <i class="fas fa-chart-bar me-2"></i>阅读统计
                </div>
                <div class="stat-item">
                    <span class="stat-label">总评分数:</span>
                    <span class="stat-value">${analysis.reading_statistics.total_ratings}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">总借阅数:</span>
                    <span class="stat-value">${analysis.reading_statistics.total_borrowings}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">平均评分:</span>
                    <span class="stat-value">${analysis.reading_statistics.average_rating.toFixed(2)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">当前借阅:</span>
                    <span class="stat-value">${analysis.reading_statistics.active_borrowings}本</span>
                </div>
            </div>
        `;

        // 偏好分析
        if (analysis.preference_analysis.favorite_categories) {
            html += `
                <div class="analysis-section">
                    <div class="analysis-title">
                        <i class="fas fa-heart me-2"></i>喜爱类别
                    </div>
                    <div>
            `;
            Object.entries(analysis.preference_analysis.favorite_categories).forEach(([category, count]) => {
                html += `<span class="preference-item">${category} (${count})</span>`;
            });
            html += '</div></div>';
        }

        // 阅读行为
        if (analysis.reading_behavior) {
            html += `
                <div class="analysis-section">
                    <div class="analysis-title">
                        <i class="fas fa-book-open me-2"></i>阅读行为
                    </div>
            `;
            
            if (analysis.reading_behavior.rating_tendency) {
                const tendencyLabels = {
                    'positive': '积极评分者',
                    'moderate': '中等评分者',
                    'critical': '挑剔评分者'
                };
                html += `
                    <div class="stat-item">
                        <span class="stat-label">评分倾向:</span>
                        <span class="stat-value">${tendencyLabels[analysis.reading_behavior.rating_tendency]}</span>
                    </div>
                `;
            }

            if (analysis.reading_behavior.average_borrow_duration) {
                html += `
                    <div class="stat-item">
                        <span class="stat-label">平均借阅天数:</span>
                        <span class="stat-value">${analysis.reading_behavior.average_borrow_duration}天</span>
                    </div>
                `;
            }

            html += '</div>';
        }

        container.innerHTML = html;

        // 显示分析区域
        document.getElementById('analysis').style.display = 'block';
        document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
    }

    async rateBook() {
        const bookId = document.getElementById('bookSelect').value;
        const rating = document.getElementById('rating').value;

        if (!this.currentUser) {
            this.showToast('请先选择用户', 'warning');
            return;
        }

        if (!bookId) {
            this.showToast('请选择图书', 'warning');
            return;
        }

        if (!rating || rating < 1 || rating > 5) {
            this.showToast('请输入有效评分(1-5)', 'warning');
            return;
        }

        try {
            this.showLoading();

            const response = await fetch(`/api/user/${this.currentUser}/rate_book`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    book_id: parseInt(bookId),
                    rating: parseInt(rating)
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showToast('评分成功', 'success');
                document.getElementById('rating').value = '';
            } else {
                throw new Error(data.error || '评分失败');
            }

        } catch (error) {
            this.showToast('评分失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async borrowBook() {
        const bookId = document.getElementById('bookSelect').value;

        if (!this.currentUser) {
            this.showToast('请先选择用户', 'warning');
            return;
        }

        if (!bookId) {
            this.showToast('请选择图书', 'warning');
            return;
        }

        try {
            this.showLoading();

            const response = await fetch(`/api/user/${this.currentUser}/borrow_book`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    book_id: parseInt(bookId)
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showToast('借阅成功', 'success');
            } else {
                throw new Error(data.error || '借阅失败');
            }

        } catch (error) {
            this.showToast('借阅失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        this.loadingModal.show();
    }

    hideLoading() {
        this.loadingModal.hide();
    }

    showToast(message, type = 'info') {
        const toastBody = document.getElementById('toastBody');
        const toastElement = document.getElementById('toast');

        // 设置样式
        toastElement.className = 'toast';
        if (type === 'success') {
            toastElement.classList.add('bg-success', 'text-white');
        } else if (type === 'error') {
            toastElement.classList.add('bg-danger', 'text-white');
        } else if (type === 'warning') {
            toastElement.classList.add('bg-warning', 'text-dark');
        }

        toastBody.textContent = message;
        this.toast.show();

        // 3秒后自动隐藏
        setTimeout(() => {
            this.toast.hide();
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new LibraryRecommendationApp();
});