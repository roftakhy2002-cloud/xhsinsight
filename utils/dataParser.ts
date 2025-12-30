
import { RawPostData, CleanPostData } from '../types';

export const cleanLikes = (val: string | number): number => {
  if (typeof val === 'number') return val;
  if (!val) return 0;
  
  const cleanStr = val.toString().trim();
  if (cleanStr.includes('万')) {
    const num = parseFloat(cleanStr.replace('万', ''));
    return Math.round(num * 10000);
  }
  
  if (cleanStr.includes('赞') || cleanStr.includes('点赞') || cleanStr === '-') {
    return 0;
  }
  
  const parsed = parseInt(cleanStr.replace(/[^0-9]/g, ''), 10);
  return isNaN(parsed) ? 0 : parsed;
};

export const parseCSV = (text: string): CleanPostData[] => {
  const lines = text.split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
  
  // Find indices for common columns
  const titleIdx = headers.findIndex(h => h.includes('title') || h.includes('标题'));
  const likesIdx = headers.findIndex(h => h.includes('likes') || h.includes('count') || h.includes('点赞'));
  const linkIdx = headers.findIndex(h => h.includes('link') || h.includes('链接'));
  const coverIdx = headers.findIndex(h => h.includes('cover') || h.includes('封面'));

  const data: CleanPostData[] = [];

  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    
    // Simple CSV split (not handling escaped commas, but for basic scrapers it's usually fine)
    // For a production app, we'd use PapaParse
    const parts = lines[i].split(',');
    
    data.push({
      id: i,
      title: parts[titleIdx] || '无标题',
      likes: cleanLikes(parts[likesIdx]),
      link: parts[linkIdx] || '',
      cover: parts[coverIdx] || ''
    });
  }

  return data;
};
