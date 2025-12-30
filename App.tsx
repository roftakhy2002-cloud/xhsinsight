
import React, { useState, useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  Upload, FileText, BarChart3, TrendingUp, Sparkles, 
  AlertCircle, CheckCircle2, Download, Award, Target, 
  Zap, ShieldAlert, BookOpen, Quote, Clock, Copy, Check
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { parseCSV } from './utils/dataParser';
import { analyzeAccount } from './services/geminiService';
import { CleanPostData, AnalysisSummary } from './types';

const App: React.FC = () => {
  const [data, setData] = useState<CleanPostData[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setReport(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result as string;
        const parsed = parseCSV(text);
        if (parsed.length === 0) {
          throw new Error("无法解析数据，请检查文件格式是否包含标题和点赞数。");
        }
        setData(parsed);
      } catch (err: any) {
        setError(err.message || "解析失败");
      } finally {
        setLoading(false);
      }
    };
    reader.readAsText(file);
  };

  const summary = useMemo((): AnalysisSummary | null => {
    if (data.length === 0) return null;
    const sortedLikes = [...data].map(d => d.likes).sort((a, b) => a - b);
    const median = sortedLikes[Math.floor(sortedLikes.length / 2)];
    let tier: '头部' | '腰部' | '尾部' = '尾部';
    if (median >= 5000) tier = '头部';
    else if (median >= 500) tier = '腰部';
    const top3 = [...data].sort((a, b) => b.likes - a.likes).slice(0, 3);
    return { medianLikes: median, totalPosts: data.length, tier, topPosts: top3 };
  }, [data]);

  const triggerAnalysis = async () => {
    if (data.length === 0) return;
    setAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeAccount(data);
      setReport(result || "生成报告失败，请重试。");
    } catch (err: any) {
      setError("AI 分析发生错误：" + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handlePrint = () => {
    // Small delay to ensure no UI feedback (like hover states) is caught in the print
    setTimeout(() => {
      window.print();
    }, 100);
  };

  const handleCopy = () => {
    if (!report) return;
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#F3F4F6] pb-20 font-sans selection:bg-red-100 selection:text-red-700">
      {/* Premium Header */}
      <header className="bg-white/80 backdrop-blur-md border-b sticky top-0 z-40 no-print">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-slate-900 p-2 rounded-xl shadow-inner">
              <BarChart3 className="text-white w-6 h-6" />
            </div>
            <div>
              <h1 className="font-black text-xl text-slate-900 tracking-tighter leading-none">XHS INSIGHT <span className="text-red-600">PRO</span></h1>
              <p className="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-400 mt-1">Strategic Account Audit</p>
            </div>
          </div>
          {data.length > 0 && (
            <div className="flex items-center gap-4">
               <button 
                 type="button"
                 onClick={triggerAnalysis}
                 disabled={analyzing}
                 className={`relative z-20 flex items-center gap-2 px-8 py-3 rounded-full font-bold text-sm transition-all shadow-xl active:scale-95 ${analyzing ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' : 'bg-red-600 hover:bg-red-700 text-white hover:shadow-red-200'}`}
               >
                 {analyzing ? (
                   <><div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div> 处理核心算法...</>
                 ) : (
                   <><Zap size={18} /> 执行深度策略诊断</>
                 )}
               </button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10">
        {/* Upload State */}
        {data.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 bg-white rounded-[2.5rem] border border-slate-200 shadow-xl shadow-slate-200/50">
            <div className="bg-red-50 p-6 rounded-full mb-8 relative">
              <Upload className="text-red-600 w-16 h-16" />
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-4 border-white animate-pulse"></div>
            </div>
            <h2 className="text-3xl font-black text-slate-900 mb-4 tracking-tight">导入原始经营数据</h2>
            <p className="text-slate-500 text-center max-w-lg mb-10 text-lg leading-relaxed">
              作为顶尖操盘手，我们只用数据说话。<br/>
              上传由插件导出的笔记详情表，开启 1:1 专家级咨询。
            </p>
            <label className="cursor-pointer group flex items-center gap-3 bg-slate-900 text-white px-12 py-5 rounded-full font-black text-lg hover:bg-slate-800 transition-all shadow-2xl hover:shadow-slate-400/50 active:scale-95">
              <FileText size={24} />
              选择数据集
              <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
            </label>
            <div className="mt-12 flex items-center gap-8 text-xs font-bold text-slate-400 uppercase tracking-widest">
               <span className="flex items-center gap-2"><Award size={16} className="text-amber-500"/> 算法驱动</span>
               <span className="flex items-center gap-2"><Target size={16} className="text-blue-500"/> 精准画像</span>
               <span className="flex items-center gap-2"><Quote size={16} className="text-red-500"/> 犀利洞察</span>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-8 bg-red-50 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-xl flex items-center gap-3 shadow-md no-print">
            <ShieldAlert size={20} />
            <span className="font-bold">{error}</span>
          </div>
        )}

        {data.length > 0 && (
          <div className="space-y-10">
            {/* Dashboard Stats Grid */}
            {!report && !analyzing && (
               <div className="grid grid-cols-1 md:grid-cols-4 gap-6 no-print">
                  {[
                    { label: '笔记总数', val: summary?.totalPosts, icon: <BookOpen />, color: 'blue' },
                    { label: '中位表现', val: summary?.medianLikes, icon: <TrendingUp />, color: 'red' },
                    { label: '流量层级', val: summary?.tier, icon: <Award />, color: 'amber' },
                    { label: '分析深度', val: '专家级', icon: <Target />, color: 'slate' }
                  ].map((s, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
                      <div className={`p-3 rounded-2xl bg-${s.color}-50 text-${s.color}-600`}>{s.icon}</div>
                      <div>
                        <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider leading-none mb-1">{s.label}</div>
                        <div className="text-xl font-black text-slate-900">{s.val}</div>
                      </div>
                    </div>
                  ))}
               </div>
            )}

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* Left Sidebar: Data Viz & Top Posts */}
              {(!report || analyzing) && (
                <div className="lg:col-span-4 space-y-8 sticky top-24 no-print">
                  <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100">
                    <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest mb-6 flex items-center gap-2">
                       <TrendingUp size={16} className="text-red-500" />
                       Growth Curve
                    </h3>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data}>
                          <defs>
                            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2}/>
                              <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                          <XAxis dataKey="id" hide />
                          <YAxis hide />
                          <Tooltip 
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}
                            labelClassName="hidden"
                          />
                          <Area type="monotone" dataKey="likes" stroke="#EF4444" strokeWidth={3} fill="url(#chartGradient)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-slate-900 text-white p-8 rounded-[2.5rem] shadow-2xl">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">High Performers</h3>
                    <div className="space-y-6">
                      {summary?.topPosts.map((post, i) => (
                        <div key={post.id} className="flex gap-4 items-start group cursor-pointer">
                          <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-black text-slate-500 border border-slate-700">
                            0{i+1}
                          </div>
                          <div className="flex-1">
                            <h4 className="text-sm font-bold text-slate-200 line-clamp-2 leading-snug group-hover:text-red-400 transition-colors">{post.title}</h4>
                            <div className="flex items-center gap-2 mt-2">
                               <span className="text-[10px] font-black bg-red-500/10 text-red-500 px-2 py-0.5 rounded uppercase tracking-tighter">{post.likes} LIKES</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Center Content: Report or Grid */}
              <div className={`${(!report || analyzing) ? 'lg:col-span-8' : 'lg:col-span-12'}`}>
                {report ? (
                  <div className="animate-in fade-in slide-in-from-bottom-6 duration-700">
                    {/* The Report Document */}
                    <article id="report-container" className="bg-white rounded-[3rem] shadow-2xl border border-slate-200 overflow-hidden print:shadow-none print:border-none print:rounded-none">
                      {/* Document Header */}
                      <div className="bg-slate-900 px-12 py-16 text-white relative overflow-hidden print:bg-black print:text-white">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-red-600/20 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl no-print"></div>
                        <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-8">
                           <div>
                             <div className="flex items-center gap-2 text-red-500 mb-4 print:text-red-600">
                               <div className="w-12 h-1 bg-red-600"></div>
                               <span className="text-xs font-black uppercase tracking-[0.3em]">CONFIDENTIAL REPORT</span>
                             </div>
                             <h2 className="text-4xl md:text-5xl font-black tracking-tight leading-none mb-4">
                               账号策略诊断报告
                             </h2>
                             <div className="flex items-center gap-6 text-slate-400 text-sm font-bold print:text-slate-500">
                               <span className="flex items-center gap-2"><Clock size={16} /> 分析时间: {new Date().toLocaleDateString()}</span>
                               <span className="flex items-center gap-2"><Target size={16} /> 样本规模: {summary?.totalPosts} 篇</span>
                             </div>
                           </div>
                           <div className="bg-white/10 backdrop-blur-md p-6 rounded-3xl border border-white/10 min-w-[200px] print:border-slate-800">
                              <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">流量分级 Verdict</div>
                              <div className="text-3xl font-black text-white">{summary?.tier}博主</div>
                              <div className="mt-2 flex items-center gap-1">
                                {[1,2,3,4,5].map(star => (
                                  <div key={star} className={`w-2 h-2 rounded-full ${star <= (summary?.tier === '头部' ? 5 : summary?.tier === '腰部' ? 3 : 2) ? 'bg-red-500' : 'bg-slate-700'}`}></div>
                                ))}
                              </div>
                           </div>
                        </div>
                      </div>

                      {/* Main Report Content */}
                      <div className="px-8 md:px-16 py-16 print:py-8">
                         {/* Executive Summary Cards */}
                         <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 print:mb-8">
                            <div className="bg-red-50 p-6 rounded-3xl border border-red-100 print:bg-white print:border-red-200">
                               <Zap className="text-red-600 mb-4 no-print" />
                               <h4 className="font-black text-slate-900 mb-2 uppercase text-xs tracking-wider">核心爆发点</h4>
                               <p className="text-sm text-slate-600 font-medium">Top 1 笔记贡献了总点赞数的 {Math.round((summary?.topPosts[0]?.likes || 0) / (data.reduce((acc, curr) => acc + curr.likes, 0) || 1) * 100)}%</p>
                            </div>
                            <div className="bg-blue-50 p-6 rounded-3xl border border-blue-100 print:bg-white print:border-blue-200">
                               <Target className="text-blue-600 mb-4 no-print" />
                               <h4 className="font-black text-slate-900 mb-2 uppercase text-xs tracking-wider">稳定性系数</h4>
                               <p className="text-sm text-slate-600 font-medium">中位值 {summary?.medianLikes} 呈现{summary?.medianLikes > 1000 ? '极强' : '中等'}抗波动能力</p>
                            </div>
                            <div className="bg-amber-50 p-6 rounded-3xl border border-amber-100 print:bg-white print:border-amber-200">
                               <Award className="text-amber-600 mb-4 no-print" />
                               <h4 className="font-black text-slate-900 mb-2 uppercase text-xs tracking-wider">爆款率</h4>
                               <p className="text-sm text-slate-600 font-medium">共发现 {data.filter(p => p.likes > (summary?.medianLikes || 0) * 3).length} 个潜在爆款节点</p>
                            </div>
                         </div>

                         {/* Markdown Render */}
                         <div className="prose prose-slate max-w-none 
                            prose-h1:text-3xl prose-h1:font-black prose-h1:tracking-tight prose-h1:border-b prose-h1:pb-4 prose-h1:mb-8
                            prose-h2:text-2xl prose-h2:font-black prose-h2:text-slate-900 prose-h2:mt-12 prose-h2:mb-6
                            prose-h3:text-xl prose-h3:font-bold prose-h3:text-red-600 prose-h3:mt-8
                            prose-p:text-slate-600 prose-p:leading-relaxed prose-p:text-lg
                            prose-strong:text-slate-900 prose-strong:font-black
                            prose-li:text-slate-600 prose-li:text-lg
                            prose-blockquote:border-red-500 prose-blockquote:bg-red-50/50 prose-blockquote:rounded-r-xl prose-blockquote:py-2 prose-blockquote:px-6
                         ">
                           <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
                         </div>
                      </div>

                      {/* Footer Signature */}
                      <div className="bg-slate-50 border-t border-slate-100 px-12 py-10 flex flex-col md:flex-row items-center justify-between gap-6 no-print">
                         <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-slate-200 border-2 border-white shadow-sm overflow-hidden flex items-center justify-center font-black text-slate-400 uppercase">OP</div>
                            <div>
                               <div className="font-black text-slate-900">首席运营架构师</div>
                               <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Digital Strategy Expert</div>
                            </div>
                         </div>
                         <div className="flex gap-4">
                            <button 
                              type="button"
                              onClick={handleCopy}
                              className="flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 shadow-sm transition-all"
                            >
                              {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                              {copied ? '已复制内容' : '复制分析文案'}
                            </button>
                            <button 
                              type="button"
                              onClick={handlePrint}
                              className="relative z-30 flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-xl text-sm font-bold hover:bg-red-700 shadow-xl transition-all"
                            >
                               <Download size={16} /> 导出 PDF 报告
                            </button>
                            <button 
                              type="button"
                              onClick={() => setReport(null)}
                              className="flex items-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-800 shadow-sm transition-all"
                            >
                               重新审计
                            </button>
                         </div>
                      </div>
                    </article>
                  </div>
                ) : analyzing ? (
                  <div className="bg-white p-20 rounded-[3rem] border border-slate-200 flex flex-col items-center justify-center text-center min-h-[600px] shadow-sm">
                    <div className="relative mb-10 scale-125">
                      <div className="w-24 h-24 border-8 border-red-50 border-t-red-600 rounded-full animate-spin"></div>
                      <Sparkles className="absolute inset-0 m-auto text-red-600 w-8 h-8 animate-pulse" />
                    </div>
                    <h2 className="text-4xl font-black text-slate-900 mb-4 tracking-tighter italic uppercase">Processing Analytics</h2>
                    <p className="text-slate-400 max-w-md text-lg font-medium">
                      正在深度拆解 {data.length} 条数据，寻找笔记中的爆发因子与流量暗线...
                    </p>
                    
                    <div className="mt-16 w-full max-w-md space-y-6">
                       {[
                         { label: '数据清洗与单位转换', color: 'green', done: true },
                         { label: '人设语义分析', progress: 'animate-progress-fast' },
                         { label: '爆款逻辑归因', progress: 'animate-progress-slow' }
                       ].map((step, idx) => (
                         <div key={idx} className="flex items-center justify-between">
                            <span className={`text-sm font-black uppercase tracking-widest ${step.done ? 'text-slate-400' : 'text-slate-900'}`}>{step.label}</span>
                            {step.done ? (
                              <CheckCircle2 size={18} className="text-green-500" />
                            ) : (
                              <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div className={`bg-red-600 h-full ${step.progress}`}></div>
                              </div>
                            )}
                         </div>
                       ))}
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-[2.5rem] shadow-sm border border-slate-100 overflow-hidden no-print">
                    <div className="px-8 py-6 bg-slate-50 border-b flex justify-between items-center">
                      <h3 className="font-black text-slate-900 text-lg flex items-center gap-2 italic uppercase tracking-tight">
                        <BarChart3 size={22} className="text-red-500"/> Raw Data Preview
                      </h3>
                      <span className="text-xs font-black text-slate-400 bg-slate-200 px-3 py-1 rounded-full">{data.length} ENTRIES</span>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="bg-white border-b text-slate-400 font-black uppercase text-[10px] tracking-[0.2em]">
                            <th className="px-8 py-5">#ID</th>
                            <th className="px-8 py-5">Content Title</th>
                            <th className="px-8 py-5">Likes</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                          {data.slice(0, 50).map((post) => (
                            <tr key={post.id} className="hover:bg-red-50/30 transition-colors group">
                              <td className="px-8 py-5 text-slate-300 font-black font-mono">{(post.id).toString().padStart(3, '0')}</td>
                              <td className="px-8 py-5 font-bold text-slate-700 group-hover:text-red-600 truncate max-w-sm transition-colors">{post.title}</td>
                              <td className="px-8 py-5 font-black text-slate-900 tabular-nums">{post.likes.toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {data.length > 50 && (
                        <div className="p-8 text-center text-slate-400 text-xs font-bold uppercase tracking-widest bg-slate-50/50">
                          ... And {data.length - 50} more records
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      <style>{`
        @keyframes progress-fast { 0% { width: 0%; } 100% { width: 100%; } }
        @keyframes progress-slow { 0% { width: 0%; } 50% { width: 60%; } 100% { width: 90%; } }
        .animate-progress-fast { animation: progress-fast 2s linear infinite; }
        .animate-progress-slow { animation: progress-slow 4s ease-in-out infinite; }
        
        @media print {
          /* Force colors and remove backgrounds */
          * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
          body { background: white !important; margin: 0 !important; padding: 0 !important; }
          header, .no-print, button, .sidebar-container { display: none !important; }
          main { width: 100% !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important; }
          #report-container { 
            box-shadow: none !important; 
            border: none !important; 
            width: 100% !important; 
            margin: 0 !important;
            padding: 0 !important;
          }
          .prose { max-width: 100% !important; font-size: 11pt !important; }
          h2, h3 { page-break-after: avoid; }
          article { break-inside: auto; }
        }
      `}</style>
    </div>
  );
};

export default App;
