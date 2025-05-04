export interface SourceCoverage {
domain: string;
original_topic_name: string;
sentiment: string;
political_leaning: string;
key_phrases: string[];
framing: string;
article_urls?: string[];
}

export interface UnifiedTopic {
name: string;
source_coverage: SourceCoverage[];
comparative_analysis: string;
}

export interface CrossSourceAnalysis {
date: string;
unified_topics: UnifiedTopic[];
}

export interface CrossSourceAnalysisResponse {
success: boolean;
date: string;
analysis: CrossSourceAnalysis | null;
created_at: string | null;
requested_date: string | null;
message?: string;
}