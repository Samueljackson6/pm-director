$Token = "MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4"
$BaseUrl = "https://agent.qcc.com/mcp/company/stream"

$Suppliers = @(
  "东莞绿光新能源科技有限公司",
  "云南省水文水资源局",
  "传申弘安智能(深圳)有限公司",
  "北京振华永创智能科技有限公司",
  "四川久越电力科技有限公司",
  "四川华城工程设计咨询有限公司",
  "四川名扬广告有限责任公司",
  "四川大川云能科技有限公司",
  "四川精宇测绘有限公司",
  "四川诺特科技有限公司",
  "国能日新科技股份有限公司",
  "天津君秒安减灾科技有限公司",
  "成都市美幻科技有限公司",
  "成都振华永创科技有限公司",
  "成都星感智联科技有限公司",
  "成都盛茂基业科技有限公司",
  "成都科宇电气设备维修有限公司",
  "成都舍南科技有限公司",
  "浙江优能电力设计有限公司",
  "淼翰数字科技(上海)有限公司",
  "绵阳杰翊图文设计有限公司",
  "西华大学",
  "西南科技大学",
  "都江堰匠筑建筑劳务有限公司",
  "重庆博宇自动化系统装置有限公司",
  "重庆理工大学",
  "四川蜀能电力有限公司高新分公司",
  "四川蜀能电科能源技术有限公司",
  "四川雅电发电有限责任公司",
  "国网四川宁南县供电有限责任公司",
  "国网四川省电力公司乐山供电公司",
  "国网四川省电力公司凉山供电公司",
  "国网四川省电力公司剑阁县供电分公司",
  "国网四川省电力公司安岳县供电分公司",
  "国网四川省电力公司富顺县供电分公司",
  "国网四川省电力公司德阳供电公司",
  "国网四川省电力公司成都供电公司",
  "国网四川省电力公司成都市青白江供电分公司",
  "国网四川省电力公司泸州供电公司",
  "国网四川省电力公司电力科学研究院",
  "国网四川省电力公司盐亭供电局",
  "国网四川省电力公司眉山供电公司",
  "国网四川省电力公司绵阳供电公司",
  "国网四川省电力公司超高压分公司",
  "国网四川省电力公司阿坝供电公司",
  "国网四川省电力公司雅安供电公司",
  "国网四川雅安电力(集团)股份有限公司荥经县供电分公司",
  "国网眉山公司",
  "成都供电公司输电管理所",
  "成都辰洲电力设备有限公司",
  "眉山市多能电力建设",
  "超高压公司成都分公司",
  "重庆供电公司市南分公司",
  "龙泉驿区规划和自然资源局"
)

Write-Host "开始批量查询 $($Suppliers.Count) 家供应商信用代码..."

foreach ($name in $Suppliers) {
  Write-Host -NoNewline "查询: $name... "
  
  $body = @{
    jsonrpc = "2.0"
    id = [int][double]::Parse((Get-Date -UFormat %s) * 1000)
    method = "tools/call"
    params = @{
      name = "get_company_by_query"
      arguments = @{ searchKey = $name }
    }
  } | ConvertTo-Json -Depth 4
  
  try {
    $response = Invoke-RestMethod -Uri $BaseUrl -Method Post -Headers @{
      "Authorization" = "Bearer $Token"
      "Content-Type" = "application/json"
    } -Body $body -TimeoutSec 10
    
    # 解析响应
    $content = $response.result.content[0].text
    $data = $content | ConvertFrom-Json
    
    if ($data.'匹配结果' -eq '单候选' -and $data.'企业信息') {
      $code = $data.'企业信息'.'统一社会信用代码'
      Write-Host "✅ $code"
    } elseif ($data.'匹配结果' -eq '多候选' -and $data.'企业信息') {
      $first = $data.'企业信息'[0]
      $code = $first.'统一社会信用代码'
      Write-Host "⚠️ 多候选, 取首个: $code"
    } else {
      Write-Host "❌ 无匹配"
    }
  } catch {
    Write-Host "💥 $_"
  }
  
  Start-Sleep -Milliseconds 500
}

Write-Host "`n查询完成!"
