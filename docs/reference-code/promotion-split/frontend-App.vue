<template>
  <div id="app">
    <!-- 推广气泡 -->
    <div class="promotion-bubble" @click="showPromotionRules">
      成为推广员
    </div>

    <!-- 主页面 -->
    <div class="container">
      <h1>商品列表</h1>
      <div class="product-list">
        <div v-for="product in products" :key="product.id" class="product-card">
          <h3>{{ product.name }}</h3>
          <p>价格: ¥{{ product.price }}</p>
          <button @click="buyProduct(product)">购买</button>
        </div>
      </div>
    </div>

    <!-- 推广规则弹窗 -->
    <div v-if="showRulesModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="showRulesModal = false">&times;</span>
        <h2>推广员规则</h2>
        <div class="rules-content">
          <p>1. 仅一级直推，无二级间推</p>
          <p>2. 收益仅来自客户真实消费订单</p>
          <p>3. 支付0.01元解锁推广权限</p>
          <p>4. 7天冻结期后自动分账</p>
          <button @click="activatePromoter" class="activate-btn">立即激活</button>
        </div>
      </div>
    </div>

    <!-- 用户协议弹窗（支付前合规告知） -->
    <div v-if="showUserAgreement" class="modal">
      <div class="modal-content">
        <h2>用户服务须知</h2>
        <div class="agreement-content">
          <p>1. 网站仅为技术撮合平台</p>
          <p>2. 商品交易双方为客户与对应推广员</p>
          <p>3. 资金第三方托管，7天冻结后自动分账</p>
          <p>4. 无拉人头返利、多级计酬活动</p>
          <div class="agreement-checkbox">
            <input type="checkbox" v-model="agreementChecked">
            <label>我已阅读并同意以上条款</label>
          </div>
          <button @click="confirmAgreement" :disabled="!agreementChecked" class="confirm-btn">确认支付</button>
        </div>
      </div>
    </div>

    <!-- 推广员后台 -->
    <div v-if="showPromoterDashboard" class="dashboard">
      <div class="dashboard-header">
        <h2>推广员后台</h2>
        <button @click="showPromoterDashboard = false">返回</button>
      </div>
      <div class="dashboard-content">
        <div class="promoter-info">
          <p>手机号: {{ promoterInfo.phone }}</p>
          <p>收款账户: {{ promoterInfo.paymentAccount }}</p>
          <p>待分账金额: ¥{{ pendingAmount }}</p>
        </div>

        <div class="section">
          <h3>推广链接</h3>
          <div class="link-box">
            <input type="text" :value="promoterLink" readonly>
            <button @click="copyLink">复制</button>
          </div>
        </div>

        <div class="section">
          <h3>名下订单</h3>
          <table class="orders-table">
            <thead>
              <tr>
                <th>订单号</th>
                <th>客户</th>
                <th>金额</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in promoterOrders" :key="order.id">
                <td>{{ order.order_no }}</td>
                <td>{{ order.customer_phone }}</td>
                <td>¥{{ order.amount }}</td>
                <td>{{ order.split_status_text }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="section">
          <h3>客户授权</h3>
          <table class="authorizations-table">
            <thead>
              <tr>
                <th>客户</th>
                <th>授权状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="auth in authorizations" :key="auth.id">
                <td>{{ auth.customer_phone }}</td>
                <td>{{ auth.authorized ? '已授权' : '未授权' }}</td>
                <td>
                  <button
                    v-if="!auth.authorized"
                    @click="authorizeCustomer(auth.customer_id, true)"
                  >
                    授权查看
                  </button>
                  <button
                    v-else
                    @click="authorizeCustomer(auth.customer_id, false)"
                  >
                    撤销授权
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      products: [
        { id: 1, name: '商品1', price: 99.9 },
        { id: 2, name: '商品2', price: 199.9 },
        { id: 3, name: '商品3', price: 299.9 }
      ],
      showRulesModal: false,
      showUserAgreement: false,
      showPromoterDashboard: false,
      agreementChecked: false,
      currentUser: null,
      promoterInfo: {},
      promoterOrders: [],
      authorizations: [],
      pendingAmount: 0,
      promoterLink: '',
      currentOrder: null
    };
  },
  created() {
    // 检查本地存储的用户信息
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      this.currentUser = JSON.parse(savedUser);
      this.checkPromoterStatus();
    }
  },
  methods: {
    // 检查推广员状态
    async checkPromoterStatus() {
      if (!this.currentUser) return;

      try {
        const response = await axios.get(`/api/user/${this.currentUser.id}`);
        if (response.data.success) {
          this.currentUser = response.data.user;
          if (this.currentUser.isPromoter) {
            await this.loadPromoterDashboard();
          }
        }
      } catch (error) {
        console.error('检查推广员状态失败:', error);
      }
    },

    // 显示推广规则
    showPromotionRules() {
      this.showRulesModal = true;
    },

    // 激活推广员
    async activatePromoter() {
      try {
        const response = await axios.post('/api/promoter/activate', {
          userId: this.currentUser.id,
          paymentAccount: '支付宝账号',
          paymentName: '收款人姓名'
        });

        if (response.data.success) {
          this.showRulesModal = false;
          alert('推广员激活成功！');
          this.currentUser.isPromoter = true;
          this.promoterInfo = {
            id: response.data.promoterId,
            phone: this.currentUser.phone,
            paymentAccount: '支付宝账号',
            paymentName: '收款人姓名'
          };
          this.promoterLink = response.data.promoterLink;
          await this.loadPromoterDashboard();
        }
      } catch (error) {
        console.error('激活推广员失败:', error);
        alert('激活推广员失败，请重试');
      }
    },

    // 加载推广员后台
    async loadPromoterDashboard() {
      try {
        const response = await axios.get(`/api/promoter/${this.promoterInfo.id}`);
        if (response.data.success) {
          this.promoterInfo = response.data.promoter;
          this.promoterOrders = response.data.orders;
          this.authorizations = response.data.authorizations;

          // 计算待分账金额
          this.pendingAmount = this.promoterOrders
            .filter(order => order.split_status_text === '待分账')
            .reduce((sum, order) => sum + order.promoter_amount, 0)
            .toFixed(2);
        }
      } catch (error) {
        console.error('加载推广员后台失败:', error);
      }
    },

    // 购买商品
    buyProduct(product) {
      if (!this.currentUser) {
        alert('请先登录');
        return;
      }

      // 查找推广关系
      axios.get(`/api/user/${this.currentUser.id}`)
        .then(response => {
          if (response.data.success) {
            const promoterId = response.data.relations.length > 0 ?
              response.data.relations[0].id : null;

            if (promoterId) {
              this.currentOrder = {
                productId: product.id,
                productName: product.name,
                price: product.price,
                promoterId: promoterId
              };
              this.showUserAgreement = true;
            } else {
              alert('请先通过推广链接访问');
            }
          }
        })
        .catch(error => {
          console.error('获取用户数据失败:', error);
          alert('获取用户数据失败');
        });
    },

    // 确认协议
    async confirmAgreement() {
      try {
        // 创建订单
        const orderResponse = await axios.post('/api/order/create', {
          userId: this.currentUser.id,
          promoterId: this.currentOrder.promoterId,
          amount: this.currentOrder.price
        });

        if (orderResponse.data.success) {
          // 支付订单
          const payResponse = await axios.post('/api/order/pay', {
            orderId: orderResponse.data.orderId
          });

          if (payResponse.data.success) {
            this.showUserAgreement = false;
            alert('支付成功！订单将在7天后自动分账');

            // 更新推广员后台数据
            if (this.currentUser.isPromoter) {
              await this.loadPromoterDashboard();
            }
          }
        }
      } catch (error) {
        console.error('创建订单失败:', error);
        alert('创建订单失败，请重试');
      }
    },

    // 客户授权
    async authorizeCustomer(customerId, authorized) {
      try {
        const response = await axios.post('/api/authorize', {
          promoterId: this.promoterInfo.id,
          customerId: customerId,
          authorized: authorized
        });

        if (response.data.success) {
          // 更新授权状态
          const auth = this.authorizations.find(a => a.customer_id === customerId);
          if (auth) {
            auth.authorized = authorized;
          }
        }
      } catch (error) {
        console.error('授权失败:', error);
        alert('授权失败，请重试');
      }
    },

    // 复制推广链接
    copyLink() {
      navigator.clipboard.writeText(this.promoterLink)
        .then(() => {
          alert('推广链接已复制');
        })
        .catch(() => {
          alert('复制失败，请手动复制');
        });
    }
  }
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.promotion-bubble {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  z-index: 1000;
}

.modal {
  position: fixed;
  z-index: 1001;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  width: 80%;
  max-width: 500px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover {
  color: black;
}

.rules-content, .agreement-content {
  margin-top: 20px;
}

.activate-btn, .confirm-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
  width: 100%;
}

.confirm-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.product-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.product-card {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 5px;
  text-align: center;
}

.product-card button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.dashboard {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: white;
  z-index: 1002;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ddd;
}

.dashboard-content {
  padding: 20px;
}

.promoter-info {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.section {
  margin-bottom: 30px;
}

.section h3 {
  margin-bottom: 15px;
}

.link-box {
  display: flex;
}

.link-box input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
}

.link-box button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.orders-table, .authorizations-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th, .orders-table td,
.authorizations-table th, .authorizations-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}

.orders-table th, .authorizations-table th {
  background-color: #f2f2f2;
}

.agreement-checkbox {
  margin: 15px 0;
}

.agreement-checkbox input {
  margin-right: 10px;
}
</style>
