// Shared types for FieldGuide AI

export interface Document {
  id: string;
  title: string;
  content: string;
  sourceOrganization: string;
  documentType: string;
  category: string;
  version: string;
  status: 'active' | 'draft' | 'archived' | 'review';
  effectiveDate: string;
  size: number;
  uploadedAt: string;
  url: string;
  uploadedByName: string;
  downloadedCount?: number;
  viewCount?: number;
}

export interface DocumentWithMetadata extends Document {
  uploadedByName: string;
  downloadedCount: number;
  viewCount: number;
}

export interface KnowledgeAnswer {
  id: string;
  question: string;
  answer: string;
  answerType: 'explanation' | 'summary' | 'recommendation' | 'comparison';
  confidence: number;
  evidence: KnowledgeEvidence[];
  followUpSuggestions: string[];
  createdAt: string;
  updatedAt: string;
}

export interface KnowledgeEvidence {
  id: string;
  sourceId: string;
  documentTitle: string;
  snippet: string;
  contentSection: string;
  citationUrl: string;
  confidenceScore: number;
  isPrimary: boolean;
  isConflicting: boolean;
  sourceOrganization: string;
  evidenceStatus: 'verified' | 'partial' | 'missing' | 'conflicting';
}

export interface ActivityItem {
  id: string;
  type: 'upload' | 'download' | 'view' | 'search' | 'escalation' | 'answer';
  title: string;
  description: string;
  timestamp: string;
  userId: string;
  documentId?: string;
  metadata?: Record<string, unknown>;
}

export interface Escalation {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  submittedDate: string;
  reviewerName: string;
  reviewerEmail: string;
  reviewerRole: string;
  documentIds: string[];
  metadata: Record<string, unknown>;
}

export interface SearchResult {
  results: Array<{
    id: string;
    type: 'document' | 'answer' | 'section';
    title: string;
    snippet: string;
    score: number;
    document?: Document;
    evidence?: KnowledgeEvidence;
  }>;
  total: number;
  timeMs: number;
}

export interface UploadResponse {
  id: string;
  title: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'analyst' | 'field_technician' | 'manager';
  avatarUrl?: string;
  initials: string;
}

export interface Toast {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  description?: string;
  duration?: number;
}

export interface Pagination {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasPrev: boolean;
  hasNext: boolean;
}

export interface APIError {
  message: string;
  details?: Record<string, string>;
  statusCode: number;
}
