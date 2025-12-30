
export interface RawPostData {
  title: string;
  likes: string | number;
  link?: string;
  cover?: string;
  [key: string]: any;
}

export interface CleanPostData {
  id: number;
  title: string;
  likes: number;
  link: string;
  cover: string;
}

export interface AnalysisSummary {
  medianLikes: number;
  totalPosts: number;
  tier: '头部' | '腰部' | '尾部';
  topPosts: CleanPostData[];
}
