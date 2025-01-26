const { createApp } = Vue

// 根据环境设置 API 地址
const API_BASE_URL = 'https://ph-translator-a0kgqwsav-enochs-projects-f32951f2.vercel.app'

createApp({
    data() {
        return {
            products: [],
            latestDate: null,
            defaultImage: 'https://placehold.co/300x200/f5f5f5/666666?text=No+Image',
            error: null,
            loading: false,
            defaultRating: 3,
            availableDates: [],
            selectedDate: null
        }
    },
    methods: {
        async fetchWithRetry(url, retries = 3) {
            for (let i = 0; i < retries; i++) {
                try {
                    return await axios.get(url)
                } catch (error) {
                    if (i === retries - 1) throw error
                    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
                }
            }
        },
        async fetchProducts() {
            this.loading = true
            this.error = null
            try {
                console.log('Fetching products...')
                const response = await this.fetchWithRetry(`${API_BASE_URL}/api/products`)
                this.products = response.data.map(product => ({
                    ...product,
                    image_url: this.validateImageUrl(product.image_url)
                }))
                console.log('Products processed:', this.products)
            } catch (error) {
                console.error('Error fetching products:', error)
                this.error = '无法加载产品数据，请稍后重试'
            } finally {
                this.loading = false
            }
        },
        async fetchLatestDate() {
            try {
                console.log('Fetching latest date...')
                const response = await axios.get(`${API_BASE_URL}/api/products/latest`)
                console.log('Latest date received:', response.data)
                this.latestDate = response.data.latest_date
            } catch (error) {
                console.error('Error fetching latest date:', error)
            }
        },
        formatDate(dateStr) {
            try {
                // 将 YYYYMMDD 格式转换为 YYYY-MM-DD
                const year = dateStr.substring(0, 4);
                const month = dateStr.substring(4, 6);
                const day = dateStr.substring(6, 8);
                const date = new Date(`${year}-${month}-${day}`);
                
                if (isNaN(date.getTime())) {
                    throw new Error('Invalid date');
                }
                
                return date.toLocaleDateString('zh-CN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            } catch (error) {
                console.error('Error formatting date:', error);
                return dateStr;
            }
        },
        handleImageError(e) {
            console.log('Image load error for:', e.target.alt);
            e.target.classList.add('error');
            if (e.target.src !== this.defaultImage) {
                e.target.src = this.defaultImage;
            }
        },
        handleImageLoad(e) {
            e.target.classList.remove('error');
            e.target.classList.add('loaded');
        },
        validateImageUrl(url) {
            if (!url || url === 'nan' || url === 'undefined') {
                return this.defaultImage;
            }
            
            // 清理 URL
            url = url.trim();
            
            if (url.startsWith('//')) {
                return 'https:' + url;
            }
            
            if (!url.startsWith('http')) {
                if (url.startsWith('/')) {
                    return 'https:/' + url;
                }
                return 'https://' + url;
            }
            
            return url;
        },
        formatPrice(price) {
            return parseFloat(price).toFixed(2)
        },
        processProduct(product) {
            return {
                ...product,
                image_url: this.validateImageUrl(product.image_url),
                rating: product.rating || this.defaultRating,
                sale: product.original_price && product.original_price > product.price,
                categories: product.categories.split('•').filter(c => c.trim())
            }
        },
        async fetchAvailableDates() {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/dates`)
                this.availableDates = response.data.dates.sort().reverse()
                if (this.availableDates.length > 0) {
                    this.selectedDate = this.availableDates[0]
                }
            } catch (error) {
                console.error('Error fetching dates:', error)
            }
        },
        async loadProductsByDate(date) {
            this.loading = true
            this.error = null
            try {
                const response = await axios.get(`${API_BASE_URL}/api/products/${date}`)
                this.products = response.data.map(this.processProduct)
            } catch (error) {
                console.error('Error loading products:', error)
                this.error = '无法加载产品数据，请稍后重试'
            } finally {
                this.loading = false
            }
        }
    },
    mounted() {
        console.log('App mounted')
        this.fetchProducts()
        this.fetchLatestDate()
        this.fetchAvailableDates()
    }
}).mount('#app') 