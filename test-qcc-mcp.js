#!/usr/bin/env node

/**
 * 企查查 MCP 测试脚本
 * 用于测试企查查 MCP 服务器的连通性和功能
 */

const https = require('https');

// 配置信息
const CONFIG = {
  baseUrl: 'https://agent.qcc.com/mcp',
  token: 'MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4',
  servers: [
    'company',
    'risk',
    'ipr',
    'operation',
    'executive',
    'history',
    'regulation',
    'case',
    'document'
  ]
};

/**
 * 发送 MCP 请求
 */
function sendMcpRequest(server, method, params = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: method,
      params: params
    });

    const options = {
      hostname: 'agent.qcc.com',
      port: 443,
      path: `/mcp/${server}/stream`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CONFIG.token}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    const req = https.request(options, (res) => {
      let body = '';

      res.on('data', (chunk) => {
        body += chunk;
      });

      res.on('end', () => {
        try {
          // 解析 SSE 格式的响应
          const lines = body.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const json = JSON.parse(line.substring(6));
              resolve(json);
              return;
            }
          }
          reject(new Error('No valid SSE data found'));
        } catch (error) {
          reject(error);
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.write(data);
    req.end();
  });
}

/**
 * 测试服务器连通性
 */
async function testConnection() {
  console.log('=== 测试 MCP 服务器连通性 ===\n');

  for (const server of CONFIG.servers) {
    try {
      const response = await sendMcpRequest(server, 'tools/list');
      const toolCount = response.result?.tools?.length || 0;
      console.log(`✅ qcc-${server}: ${toolCount} 个工具可用`);
    } catch (error) {
      console.log(`❌ qcc-${server}: 连接失败 - ${error.message}`);
    }
  }

  console.log('');
}

/**
 * 测试企业查询
 */
async function testCompanyQuery(keyword) {
  console.log(`\n=== 测试企业查询: ${keyword} ===\n`);

  try {
    // 1. 企业实体识别
    console.log('1. 执行企业实体识别...');
    const queryResult = await sendMcpRequest('company', 'tools/call', {
      name: 'get_company_by_query',
      arguments: { searchKey: keyword }
    });

    const queryData = JSON.parse(queryResult.result.content[0].text);

    if (queryData.匹配结果 === '多候选') {
      console.log(`\n找到 ${queryData.企业信息.length} 个候选企业:\n`);
      queryData.企业信息.forEach((company, index) => {
        console.log(`${index + 1}. ${company.企业名称}`);
        console.log(`   统一社会信用代码: ${company.统一社会信用代码}`);
        console.log(`   法定代表人: ${company.法定代表人名称.join(', ')}`);
        console.log(`   状态: ${company.状态}`);
        console.log(`   成立日期: ${company.成立日期}\n`);
      });

      return queryData.企业信息[0].统一社会信用代码;
    } else {
      console.log(`\n唯一匹配: ${queryData.企业名称}`);
      console.log(`统一社会信用代码: ${queryData.统一社会信用代码}\n`);
      return queryData.统一社会信用代码;
    }
  } catch (error) {
    console.error('企业查询失败:', error.message);
    return null;
  }
}

/**
 * 测试企业详情
 */
async function testCompanyDetail(creditCode) {
  if (!creditCode) {
    console.log('跳过企业详情测试: 无有效统一社会信用代码');
    return;
  }

  console.log('\n=== 测试企业详情查询 ===\n');

  try {
    // 查询工商信息
    console.log('1. 查询工商信息...');
    const regResult = await sendMcpRequest('company', 'tools/call', {
      name: 'get_company_registration_info',
      arguments: { searchKey: creditCode }
    });

    const regData = JSON.parse(regResult.result.content[0].text);
    console.log(`\n企业名称: ${regData.企业名称}`);
    console.log(`法定代表人: ${regData.法定代表人}`);
    console.log(`注册资本: ${regData.注册资本}`);
    console.log(`成立日期: ${regData.成立日期}`);
    console.log(`登记状态: ${regData.登记状态}`);
    console.log(`注册地址: ${regData.注册地址}`);

    // 查询风险扫描
    console.log('\n2. 执行风险扫描...');
    const riskResult = await sendMcpRequest('risk', 'tools/call', {
      name: 'get_company_risk_scan',
      arguments: { searchKey: creditCode }
    });

    const riskData = JSON.parse(riskResult.result.content[0].text);
    console.log(`\n风险扫描摘要: ${riskData.摘要}`);

    // 查询商标信息
    console.log('\n3. 查询商标信息...');
    const iprResult = await sendMcpRequest('ipr', 'tools/call', {
      name: 'get_trademark_info',
      arguments: { searchKey: creditCode }
    });

    const iprData = JSON.parse(iprResult.result.content[0].text);
    console.log(`\n商标信息: ${iprData.摘要}`);

  } catch (error) {
    console.error('企业详情查询失败:', error.message);
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('\n企查查 MCP 测试脚本\n');
  console.log('========================\n');

  // 测试连通性
  await testConnection();

  // 测试企业查询
  const creditCode = await testCompanyQuery('腾讯');

  // 测试企业详情
  await testCompanyDetail(creditCode);

  console.log('\n\n测试完成！\n');
}

// 运行测试
main().catch(console.error);
