export interface Summary {
    domain: string;
    language: string;
    date: string;
    content: string;
  }
  
  export interface SummaryApiResponse {
    summaries: Summary[];
    success: boolean;
  }