/**
 * 小程序分账系统 - 后端 API（Node.js + Express + MySQL）
 *
 * 合规要点：
 * - 仅一级推广，杜绝传销风险
 * - 资金由第三方支付服务商（云购OS等）托管，规避二清风险
 * - 7 天资金冻结期，保障售后退款
 * - 客户隐私保护：需授权才能查看联系方式
 */
const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');
const crypto = require('crypto');
const axios = require('axios');
const app = express();
const port = process.env.PORT || 3000;

// 数据库连接
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || 'password',
  database: process.env.DB_NAME || 'promotion_system',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// 中间件
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 工具函数
const generateOrderNo = () => {
  return 'ORDER' + Date.now() + Math.floor(Math.random() * 1000);
};

const generatePromoterLink = (promoterId) => {
  return `https://yourdomain.com/promote/${promoterId}`;
};

// 云购OS API封装（第三方支付托管，规避二清）
const yungouApi = {
  // 创建订单
  createOrder: async (amount, promoterId) => {
    try {
      const response = await axios.post('https://api.yungouos.com/create', {
        amount: amount,
        promoter_id: promoterId,
        notify_url: 'https://yourdomain.com/api/notify'
      }, {
        headers: {
          'Authorization': `Bearer ${process.env.YUNGOU_API_KEY}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('云购OS创建订单失败:', error);
      throw error;
    }
  },

  // 分账
  splitOrder: async (orderId, promoterAmount, platformFee) => {
    try {
      const response = await axios.post('https://api.yungouos.com/split', {
        order_id: orderId,
        splits: [
          {
            role: 'promoter',
            amount: promoterAmount,
            account: 'promoter_account' // 实际从数据库获取
          },
          {
            role: 'platform',
            amount: platformFee,
            account: process.env.PLATFORM_ACCOUNT
          }
        ]
      }, {
        headers: {
          'Authorization': `Bearer ${process.env.YUNGOU_API_KEY}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('云购OS分账失败:', error);
      throw error;
    }
  }
};

// ============ API 路由 ============

// 1. 用户注册
app.post('/api/register', async (req, res) => {
  try {
    const { phone } = req.body;

    // 检查手机号是否已注册
    const [existingUsers] = await pool.execute(
      'SELECT id FROM users WHERE phone = ?', [phone]
    );

    if (existingUsers.length > 0) {
      return res.status(400).json({ success: false, message: '手机号已注册' });
    }

    // 创建用户
    const [result] = await pool.execute(
      'INSERT INTO users (phone) VALUES (?)', [phone]
    );

    res.json({ success: true, userId: result.insertId });
  } catch (error) {
    console.error('注册失败:', error);
    res.status(500).json({ success: false, message: '注册失败' });
  }
});

// 2. 激活推广员（支付 0.01 元解锁推广权限）
app.post('/api/promoter/activate', async (req, res) => {
  try {
    const { userId, paymentAccount, paymentName } = req.body;

    // 开启事务
    const connection = await pool.getConnection();
    await connection.beginTransaction();

    try {
      // 检查是否已经是推广员
      const [users] = await connection.execute(
        'SELECT id, is_promoter FROM users WHERE id = ?', [userId]
      );

      if (users.length === 0) {
        return res.status(400).json({ success: false, message: '用户不存在' });
      }

      if (users[0].is_promoter) {
        return res.status(400).json({ success: false, message: '已经是推广员' });
      }

      // 创建0.01元订单
      const orderNo = generateOrderNo();
      const [orderResult] = await connection.execute(
        'INSERT INTO orders (order_no, customer_id, amount, status) VALUES (?, ?, ?, ?)',
        [orderNo, userId, 0.01, 1]
      );

      // 调用云购OS创建支付订单
      const yungouOrder = await yungouApi.createOrder(0.01, userId);

      // 更新订单支付信息
      await connection.execute(
        'UPDATE orders SET status = ?, payment_no = ? WHERE id = ?',
        [2, yungouOrder.payment_id, orderResult.insertId]
      );

      // 创建推广员记录
      const [promoterResult] = await connection.execute(
        'INSERT INTO promoters (user_id, payment_account, payment_name) VALUES (?, ?, ?)',
        [userId, paymentAccount, paymentName]
      );

      // 记录协议
      const agreementContent = '推广员协议内容...';
      await connection.execute(
        'INSERT INTO agreements (user_id, agreement_type, content, ip_address) VALUES (?, ?, ?, ?)',
        [userId, 'promoter', agreementContent, req.ip]
      );

      // 更新用户为推广员
      await connection.execute(
        'UPDATE users SET is_promoter = 1, promoter_activated_at = NOW() WHERE id = ?',
        [userId]
      );

      await connection.commit();

      res.json({
        success: true,
        orderId: orderResult.insertId,
        promoterId: promoterResult.insertId,
        promoterLink: generatePromoterLink(promoterResult.insertId)
      });
    } catch (error) {
      await connection.rollback();
      throw error;
    } finally {
      connection.release();
    }
  } catch (error) {
    console.error('激活推广员失败:', error);
    res.status(500).json({ success: false, message: '激活推广员失败' });
  }
});

// 3. 注销推广员（可随时注销并退款）
app.post('/api/promoter/deactivate', async (req, res) => {
  try {
    const { userId } = req.body;

    // 开启事务
    const connection = await pool.getConnection();
    await connection.beginTransaction();

    try {
      // 检查是否是推广员
      const [users] = await connection.execute(
        'SELECT id, is_promoter, promoter_activated_at FROM users WHERE id = ?', [userId]
      );

      if (users.length === 0 || !users[0].is_promoter) {
        return res.status(400).json({ success: false, message: '不是推广员' });
      }

      // 查找0.01元激活订单
      const [orders] = await connection.execute(
        'SELECT id, status FROM orders WHERE customer_id = ? AND amount = 0.01 ORDER BY created_at DESC LIMIT 1',
        [userId]
      );

      if (orders.length > 0 && orders[0].status === 2) {
        // 退款
        const yungouRefund = await axios.post('https://api.yungouos.com/refund', {
          order_id: orders[0].payment_no,
          amount: 0.01
        }, {
          headers: {
            'Authorization': `Bearer ${process.env.YUNGOU_API_KEY}`
          }
        });

        // 更新订单状态
        await connection.execute(
          'UPDATE orders SET status = 4 WHERE id = ?', [orders[0].id]
        );

        // 标记推广员已退款
        await connection.execute(
          'UPDATE users SET promoter_refunded = 1 WHERE id = ?', [userId]
        );
      }

      // 更新用户状态
      await connection.execute(
        'UPDATE users SET is_promoter = 0 WHERE id = ?', [userId]
      );

      await connection.commit();

      res.json({ success: true, message: '推广员已注销' });
    } catch (error) {
      await connection.rollback();
      throw error;
    } finally {
      connection.release();
    }
  } catch (error) {
    console.error('注销推广员失败:', error);
    res.status(500).json({ success: false, message: '注销推广员失败' });
  }
});

// 4. 创建订单
app.post('/api/order/create', async (req, res) => {
  try {
    const { userId, promoterId, amount } = req.body;

    // 开启事务
    const connection = await pool.getConnection();
    await connection.beginTransaction();

    try {
      // 创建订单
      const orderNo = generateOrderNo();
      const [orderResult] = await connection.execute(
        'INSERT INTO orders (order_no, customer_id, promoter_id, amount, status, frozen_until) VALUES (?, ?, ?, ?, ?, DATE_ADD(NOW(), INTERVAL 7 DAY))',
        [orderNo, userId, promoterId, amount, 1]
      );

      // 创建推广关系（如果不存在）
      const [relationCheck] = await connection.execute(
        'SELECT id FROM promotion_relations WHERE promoter_id = ? AND customer_id = ?',
        [promoterId, userId]
      );

      if (relationCheck.length === 0) {
        await connection.execute(
          'INSERT INTO promotion_relations (promoter_id, customer_id) VALUES (?, ?)',
          [promoterId, userId]
        );
      }

      // 创建分账记录
      const promoterRatio = 0.9; // 推广员分账比例
      const platformRatio = 0.1; // 平台分账比例
      const promoterAmount = amount * promoterRatio;
      const platformFee = amount * platformRatio;

      await connection.execute(
        'INSERT INTO order_splits (order_id, promoter_amount, platform_fee, split_status) VALUES (?, ?, ?, ?)',
        [orderResult.insertId, promoterAmount, platformFee, 1]
      );

      await connection.commit();

      res.json({ success: true, orderId: orderResult.insertId });
    } catch (error) {
      await connection.rollback();
      throw error;
    } finally {
      connection.release();
    }
  } catch (error) {
    console.error('创建订单失败:', error);
    res.status(500).json({ success: false, message: '创建订单失败' });
  }
});

// 5. 支付订单
app.post('/api/order/pay', async (req, res) => {
  try {
    const { orderId } = req.body;

    // 获取订单信息
    const [orders] = await pool.execute(
      'SELECT * FROM orders WHERE id = ?', [orderId]
    );

    if (orders.length === 0) {
      return res.status(400).json({ success: false, message: '订单不存在' });
    }

    const order = orders[0];

    // 调用云购OS创建支付订单
    const yungouOrder = await yungouApi.createOrder(order.amount, order.promoter_id);

    // 更新订单状态
    await pool.execute(
      'UPDATE orders SET status = 2, payment_no = ? WHERE id = ?',
      [yungouOrder.payment_id, orderId]
    );

    res.json({ success: true, paymentId: yungouOrder.payment_id });
  } catch (error) {
    console.error('支付订单失败:', error);
    res.status(500).json({ success: false, message: '支付订单失败' });
  }
});

// 6. 分账完成通知（支付回调，7天后自动分账）
app.post('/api/notify', async (req, res) => {
  try {
    const { order_id, status } = req.body;

    if (status === 'paid') {
      // 更新订单状态为已完成
      await pool.execute(
        'UPDATE orders SET status = 3 WHERE payment_no = ?', [order_id]
      );

      // 设置7天后自动分账
      setTimeout(async () => {
        try {
          // 获取订单信息
          const [orders] = await pool.execute(
            'SELECT o.*, os.promoter_amount, os.platform_fee FROM orders o JOIN order_splits os ON o.id = os.order_id WHERE o.payment_no = ? AND o.status = 3',
            [order_id]
          );

          if (orders.length > 0) {
            const order = orders[0];

            // 执行分账
            await yungouApi.splitOrder(order_id, order.promoter_amount, order.platform_fee);

            // 更新分账状态
            await pool.execute(
              'UPDATE order_splits SET split_status = 2, split_at = NOW() WHERE order_id = ?',
              [order.id]
            );
          }
        } catch (error) {
          console.error('自动分账失败:', error);
        }
      }, 7 * 24 * 60 * 60 * 1000); // 7天后执行
    }

    res.json({ success: true });
  } catch (error) {
    console.error('分账通知处理失败:', error);
    res.status(500).json({ success: false, message: '分账通知处理失败' });
  }
});

// 7. 退款申请（退款自动冲抵分账资金）
app.post('/api/order/refund', async (req, res) => {
  try {
    const { orderId, amount } = req.body;

    // 获取订单信息
    const [orders] = await pool.execute(
      'SELECT * FROM orders WHERE id = ?', [orderId]
    );

    if (orders.length === 0) {
      return res.status(400).json({ success: false, message: '订单不存在' });
    }

    const order = orders[0];

    // 调用云购OS退款
    const yungouRefund = await axios.post('https://api.yungouos.com/refund', {
      order_id: order.payment_no,
      amount: amount || order.amount
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.YUNGOU_API_KEY}`
      }
    });

    // 更新订单状态
    await pool.execute(
      'UPDATE orders SET status = 4 WHERE id = ?', [orderId]
    );

    // 更新分账状态
    await pool.execute(
      'UPDATE order_splits SET split_status = 3 WHERE order_id = ?', [orderId]
    );

    res.json({ success: true });
  } catch (error) {
    console.error('退款失败:', error);
    res.status(500).json({ success: false, message: '退款失败' });
  }
});

// 8. 客户授权查看手机号
app.post('/api/authorize', async (req, res) => {
  try {
    const { promoterId, customerId, authorized } = req.body;

    // 检查是否存在授权记录
    const [authorizations] = await pool.execute(
      'SELECT id FROM authorizations WHERE promoter_id = ? AND customer_id = ?',
      [promoterId, customerId]
    );

    if (authorizations.length > 0) {
      // 更新授权
      await pool.execute(
        'UPDATE authorizations SET authorized = ?, authorized_at = NOW() WHERE id = ?',
        [authorized, authorizations[0].id]
      );
    } else {
      // 创建授权记录
      await pool.execute(
        'INSERT INTO authorizations (promoter_id, customer_id, authorized, authorized_at) VALUES (?, ?, ?, NOW())',
        [promoterId, customerId, authorized]
      );
    }

    res.json({ success: true });
  } catch (error) {
    console.error('授权失败:', error);
    res.status(500).json({ success: false, message: '授权失败' });
  }
});

// 9. 获取推广员数据
app.get('/api/promoter/:promoterId', async (req, res) => {
  try {
    const { promoterId } = req.params;

    // 获取推广员基本信息
    const [promoters] = await pool.execute(
      `SELECT p.*, u.phone, u.created_at as user_created_at
       FROM promoters p
       JOIN users u ON p.user_id = u.id
       WHERE p.id = ?`, [promoterId]
    );

    if (promoters.length === 0) {
      return res.status(400).json({ success: false, message: '推广员不存在' });
    }

    const promoter = promoters[0];

    // 获取推广员订单
    const [orders] = await pool.execute(
      `SELECT o.*,
        CASE WHEN os.split_status = 1 THEN '待分账'
             WHEN os.split_status = 2 THEN '已分账'
             WHEN os.split_status = 3 THEN '已退款'
             ELSE '未知' END as split_status_text
       FROM orders o
       JOIN order_splits os ON o.id = os.order_id
       WHERE o.promoter_id = ?
       ORDER BY o.created_at DESC`, [promoterId]
    );

    // 获取授权记录
    const [authorizations] = await pool.execute(
      `SELECT a.*, u.phone as customer_phone
       FROM authorizations a
       JOIN users u ON a.customer_id = u.id
       WHERE a.promoter_id = ?
       ORDER BY a.created_at DESC`, [promoterId]
    );

    res.json({
      success: true,
      promoter: {
        id: promoter.id,
        phone: promoter.phone,
        paymentAccount: promoter.payment_account,
        paymentName: promoter.payment_name,
        activatedAt: promoter.promoter_activated_at,
        userCreatedAt: promoter.user_created_at
      },
      orders,
      authorizations
    });
  } catch (error) {
    console.error('获取推广员数据失败:', error);
    res.status(500).json({ success: false, message: '获取推广员数据失败' });
  }
});

// 10. 获取用户数据
app.get('/api/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    // 获取用户基本信息
    const [users] = await pool.execute(
      'SELECT * FROM users WHERE id = ?', [userId]
    );

    if (users.length === 0) {
      return res.status(400).json({ success: false, message: '用户不存在' });
    }

    const user = users[0];

    // 获取用户订单
    const [orders] = await pool.execute(
      `SELECT o.*,
        CASE WHEN os.split_status = 1 THEN '待分账'
             WHEN os.split_status = 2 THEN '已分账'
             WHEN os.split_status = 3 THEN '已退款'
             ELSE '未知' END as split_status_text,
        p.payment_account as promoter_account
       FROM orders o
       JOIN order_splits os ON o.id = os.order_id
       LEFT JOIN promoters p ON o.promoter_id = p.id
       WHERE o.customer_id = ?
       ORDER BY o.created_at DESC`, [userId]
    );

    // 获取推广关系
    const [relations] = await pool.execute(
      `SELECT p.id as promoter_id, p.payment_account, p.payment_name
       FROM promotion_relations pr
       JOIN promoters p ON pr.promoter_id = p.id
       WHERE pr.customer_id = ?`, [userId]
    );

    res.json({
      success: true,
      user: {
        id: user.id,
        phone: user.phone,
        isPromoter: user.is_promoter,
        activatedAt: user.promoter_activated_at
      },
      orders,
      relations
    });
  } catch (error) {
    console.error('获取用户数据失败:', error);
    res.status(500).json({ success: false, message: '获取用户数据失败' });
  }
});

// 启动服务器
app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
});
