/**
 * 定时任务（分账处理）- node-cron
 *
 * - 每天凌晨2点：检查 7 天冻结期已满的订单，执行自动分账
 * - 每天凌晨3点：检查已退款订单，更新分账状态为已退款
 */
const cron = require('node-cron');

// 每天凌晨2点检查需要分账的订单
cron.schedule('0 2 * * *', async () => {
  try {
    const connection = await pool.getConnection();
    await connection.beginTransaction();

    try {
      // 查找7天前已完成但未分账的订单
      const [orders] = await connection.execute(
        `SELECT o.*, os.promoter_amount, os.platform_fee, p.payment_account as promoter_account
         FROM orders o
         JOIN order_splits os ON o.id = os.order_id
         JOIN promoters p ON o.promoter_id = p.id
         WHERE o.status = 3
           AND os.split_status = 1
           AND o.frozen_until < NOW()`
      );

      for (const order of orders) {
        try {
          // 执行分账
          await yungouApi.splitOrder(order.payment_no, order.promoter_amount, order.platform_fee);

          // 更新分账状态
          await connection.execute(
            'UPDATE order_splits SET split_status = 2, split_at = NOW() WHERE order_id = ?',
            [order.id]
          );

          console.log(`订单 ${order.id} 分账成功`);
        } catch (error) {
          console.error(`订单 ${order.id} 分账失败:`, error);
        }
      }

      await connection.commit();
    } catch (error) {
      await connection.rollback();
      console.error('定时分账任务失败:', error);
    } finally {
      connection.release();
    }
  } catch (error) {
    console.error('获取数据库连接失败:', error);
  }
});

// 每天凌晨3点检查需要退款的订单
cron.schedule('0 3 * * *', async () => {
  try {
    const connection = await pool.getConnection();
    await connection.beginTransaction();

    try {
      // 查找已退款但未更新分账状态的订单
      const [orders] = await connection.execute(
        `SELECT o.*, os.promoter_amount, os.platform_fee
         FROM orders o
         JOIN order_splits os ON o.id = os.order_id
         WHERE o.status = 4
           AND os.split_status = 1`
      );

      for (const order of orders) {
        try {
          // 更新分账状态为已退款
          await connection.execute(
            'UPDATE order_splits SET split_status = 3 WHERE order_id = ?',
            [order.id]
          );

          console.log(`订单 ${order.id} 退款处理完成`);
        } catch (error) {
          console.error(`订单 ${order.id} 退款处理失败:`, error);
        }
      }

      await connection.commit();
    } catch (error) {
      await connection.rollback();
      console.error('定时退款任务失败:', error);
    } finally {
      connection.release();
    }
  } catch (error) {
    console.error('获取数据库连接失败:', error);
  }
});
