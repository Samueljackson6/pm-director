const https = require('https');

const TOKEN = 'MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4';
const BASE_URL = 'https://agent.qcc.com/mcp/company/stream';

// 7家已通过多候选匹配到信用代码的供应商
const SUPPLIERS_WITH_CODE = [
  { name: '国网四川省电力公司盐亭供电局', creditCode: '91510000621601108W' },
  { name: '国网眉山公司', creditCode: '91511400733418746W' },
  { name: '成都供电公司输电管理所', creditCode: '91510107MACBAL3G0W' },
  { name: '眉山市多能电力建设', creditCode: '915114007469274007' },
  { name: '超高压公司成都分公司', creditCode: '91510000675760294C' },
  { name: '重庆供电公司市南分公司', creditCode: '91500000902877135D' },
  { name: '龙泉驿区规划和自然资源局', creditCode: '81510112MC56590864' }
];

async function queryByCreditCode(code) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: { name: 'get_company_registration_info', arguments: { searchKey: code } }
    });

    const options = {
      hostname: 'agent.qcc.com',
      port: 443,
      path: '/mcp/company/stream',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const lines = body.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const json = JSON.parse(line.substring(6));
              const text = JSON.parse(json.result.content[0].text);
              resolve(text);
              return;
            }
          }
          reject(new Error('No valid SSE data'));
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function main() {
  console.log('开始用信用代码查询企业基本信息...\n');
  
  for (const sup of SUPPLIERS_WITH_CODE) {
    console.log(`查询: ${sup.name} (${sup.creditCode})`);
    
    try {
      const data = await queryByCreditCode(sup.creditCode);
      
      if (data && data['企业名称']) {
        console.log(`  ✅ 企业名称: ${data['企业名称']}`);
        console.log(`  ✅ 法定代表人: ${data['法定代表人']}`);
        console.log(`  ✅ 注册资本: ${data['注册资本']}`);
        console.log(`  ✅ 成立日期: ${data['成立日期']}`);
        console.log(`  ✅ 登记状态: ${data['登记状态']}`);
        console.log(`  ✅ 注册地址: ${data['注册地址']}`);
        console.log(`  ✅ 经营范围: ${data['经营范围']}`);
      } else {
        console.log('  ❌ 无数据');
      }
    } catch (err) {
      console.log(`  💥 ${err.message}`);
    }
    
    console.log('');
    await new Promise(r => setTimeout(r, 500));
  }
}

main().catch(console.error);
