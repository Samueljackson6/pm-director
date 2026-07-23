const https = require('https');

const TOKEN = 'MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4';
const BASE_URL = 'https://agent.qcc.com/mcp/company/stream';

const SUPPLIERS = [
  '东莞绿光新能源科技有限公司',
  '云南省水文水资源局',
  '传申弘安智能(深圳)有限公司',
  '北京振华永创智能科技有限公司',
  '四川久越电力科技有限公司',
  '四川华城工程设计咨询有限公司',
  '四川名扬广告有限责任公司',
  '四川大川云能科技有限公司',
  '四川精宇测绘有限公司',
  '四川诺特科技有限公司',
  '国能日新科技股份有限公司',
  '天津君秒安减灾科技有限公司',
  '成都市美幻科技有限公司',
  '成都振华永创科技有限公司',
  '成都星感智联科技有限公司',
  '成都盛茂基业科技有限公司',
  '成都科宇电气设备维修有限公司',
  '成都舍南科技有限公司',
  '浙江优能电力设计有限公司',
  '淼翰数字科技(上海)有限公司',
  '绵阳杰翊图文设计有限公司',
  '西华大学',
  '西南科技大学',
  '都江堰匠筑建筑劳务有限公司',
  '重庆博宇自动化系统装置有限公司',
  '重庆理工大学',
  '四川蜀能电力有限公司高新分公司',
  '四川蜀能电科能源技术有限公司',
  '四川雅电发电有限责任公司',
  '国网四川宁南县供电有限责任公司',
  '国网四川省电力公司乐山供电公司',
  '国网四川省电力公司凉山供电公司',
  '国网四川省电力公司剑阁县供电分公司',
  '国网四川省电力公司安岳县供电分公司',
  '国网四川省电力公司富顺县供电分公司',
  '国网四川省电力公司德阳供电公司',
  '国网四川省电力公司成都供电公司',
  '国网四川省电力公司成都市青白江供电分公司',
  '国网四川省电力公司泸州供电公司',
  '国网四川省电力公司电力科学研究院',
  '国网四川省电力公司盐亭供电局',
  '国网四川省电力公司眉山供电公司',
  '国网四川省电力公司绵阳供电公司',
  '国网四川省电力公司超高压分公司',
  '国网四川省电力公司阿坝供电公司',
  '国网四川省电力公司雅安供电公司',
  '国网四川雅安电力(集团)股份有限公司荥经县供电分公司',
  '国网眉山公司',
  '成都供电公司输电管理所',
  '成都辰洲电力设备有限公司',
  '眉山市多能电力建设',
  '超高压公司成都分公司',
  '重庆供电公司市南分公司',
  '龙泉驿区规划和自然资源局'
];

async function queryByName(keyword) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: { name: 'get_company_by_query', arguments: { searchKey: keyword } }
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
  console.log(`开始批量查询 ${SUPPLIERS.length} 家供应商信用代码...\n`);
  
  const results = [];
  
  for (let i = 0; i < SUPPLIERS.length; i++) {
    const name = SUPPLIERS[i];
    process.stdout.write(`[${i + 1}/${SUPPLIERS.length}] ${name}...`);
    
    try {
      const data = await queryByName(name);
      
      if (data['匹配结果'] === '单候选' && data['企业信息']) {
        const company = data['企业信息'];
        const code = company['统一社会信用代码'];
        console.log(` ✅ ${code}`);
        results.push({ name, creditCode: code, status: 'found' });
      } else if (data['匹配结果'] === '多候选' && data['企业信息']) {
        const first = data['企业信息'][0];
        const code = first['统一社会信用代码'];
        console.log(` ⚠️ 多候选, 取首个: ${code}`);
        results.push({ name, creditCode: code, status: 'multi_first' });
      } else {
        console.log(` ❌ 无匹配`);
        results.push({ name, creditCode: '', status: 'none' });
      }
    } catch (err) {
      console.log(` 💥 ${err.message}`);
      results.push({ name, creditCode: '', status: 'error', error: err.message });
    }
    
    if (i < SUPPLIERS.length - 1) {
      await new Promise(r => setTimeout(r, 500));
    }
  }
  
  // 输出汇总
  console.log('\n\n========== 汇总 ==========');
  let found = 0, multi = 0, none = 0, error = 0;
  for (const r of results) {
    if (r.status === 'found') found++;
    else if (r.status === 'multi_first') multi++;
    else if (r.status === 'none') none++;
    else error++;
  }
  console.log(`✅ 单候选: ${found}`);
  console.log(`⚠️ 多候选(取首个): ${multi}`);
  console.log(`❌ 无匹配: ${none}`);
  console.log(`💥 错误: ${error}`);
  
  // 保存结果
  const fs = require('fs');
  fs.writeFileSync('scripts/qcc_credit_codes.json', JSON.stringify(results, null, 2), 'utf-8');
  console.log('\n结果已保存至 scripts/qcc_credit_codes.json');
}

main().catch(console.error);
