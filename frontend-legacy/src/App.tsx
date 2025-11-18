import { Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import { Upload } from 'lucide-react';
import { ParameterGathering } from './components/ParameterGathering';
import { AgentWorkflow } from './components/AgentWorkflow';
import { ForecastSummary } from './components/ForecastSummary';
import { ClusterCards } from './components/ClusterCards';
import { WeeklyPerformanceChart } from './components/WeeklyPerformanceChart';
import { ReplenishmentQueue } from './components/ReplenishmentQueue';
import { MarkdownDecision } from './components/MarkdownDecision';
import { PerformanceMetrics } from './components/PerformanceMetrics';
import { AppLayout } from './components/Layout';
import { SectionHeader } from './components/Layout/SectionHeader';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useParameters } from './contexts/ParametersContext';
import { ReportPage } from './pages/ReportPage';
import { UploadModal } from './components/UploadModal';
import { Button } from './components/ui/button';

function Dashboard() {
  const { parameters, workflowId } = useParameters();
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  // Parameters gathering page (no sidebar)
  if (!parameters) {
    return (
      <AppLayout showSidebar={false} breadcrumbs={[]}>
        <div className="max-w-4xl mx-auto">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-text-primary mb-2">
              Multi-Agent Retail Forecasting
            </h1>
            <p className="text-text-secondary">
              Phase 2 - Frontend Implementation
            </p>
          </header>
          <ParameterGathering />
        </div>
      </AppLayout>
    );
  }

  // Dashboard with sidebar navigation
  return (
    <AppLayout breadcrumbs={[{ label: 'Spring 2025 Dashboard' }]}>
      {/* Section 0: Parameters (hidden after gathering) */}
      <section id="parameters" className="mb-12">
        <SectionHeader
          id="parameters-header"
          title="Parameters"
          description="Extracted season parameters"
          icon="⚙️"
        />
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-text-secondary">Forecast Horizon:</span>{' '}
              <span className="text-text-primary font-mono">{parameters.forecast_horizon_weeks} weeks</span>
            </div>
            <div>
              <span className="text-text-secondary">Season Start:</span>{' '}
              <span className="text-text-primary font-mono">{parameters.season_start_date}</span>
            </div>
            <div>
              <span className="text-text-secondary">Season End:</span>{' '}
              <span className="text-text-primary font-mono">{parameters.season_end_date}</span>
            </div>
            <div>
              <span className="text-text-secondary">Replenishment:</span>{' '}
              <span className="text-text-primary font-mono">{parameters.replenishment_strategy}</span>
            </div>
            <div>
              <span className="text-text-secondary">DC Holdback:</span>{' '}
              <span className="text-text-primary font-mono">{parameters.dc_holdback_percentage}%</span>
            </div>
            <div>
              <span className="text-text-secondary">Confidence:</span>{' '}
              <span className="text-text-primary font-mono">{parameters.extraction_confidence}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 1: Agent Workflow */}
      <section id="agents" className="mb-12">
        <SectionHeader
          id="agents-header"
          title="Agent Workflow"
          description="Multi-agent system execution status"
          icon="🤖"
        />
        <ErrorBoundary>
          <AgentWorkflow workflowId={workflowId} />
        </ErrorBoundary>
      </section>

      {/* Upload Data Button (only visible when workflowId exists) */}
      {workflowId && (
        <div className="flex justify-center mb-12">
          <Button
            onClick={() => setUploadModalOpen(true)}
            variant="outline"
            size="lg"
            className="gap-2"
            aria-label="Upload CSV data files for agents"
          >
            <Upload className="w-5 h-5" />
            Upload CSV Data (Optional)
          </Button>
        </div>
      )}

      {/* Section 2: Forecast Summary */}
      <section id="forecast" className="mb-12">
        <SectionHeader
          id="forecast-header"
          title="Forecast Summary"
          description="Season demand forecast and key metrics"
          icon="📊"
        />
        <ErrorBoundary>
          <ForecastSummary />
        </ErrorBoundary>
      </section>

      {/* Section 3: Cluster Distribution */}
      <section id="clusters" className="mb-12">
        <SectionHeader
          id="clusters-header"
          title="Cluster Distribution"
          description="Store clustering and allocation breakdown"
          icon="🏪"
        />
        <ErrorBoundary>
          <ClusterCards />
        </ErrorBoundary>
      </section>

      {/* Section 4: Weekly Performance */}
      <section id="weekly" className="mb-12">
        <SectionHeader
          id="weekly-header"
          title="Weekly Performance"
          description="Forecast vs actuals with variance analysis"
          icon="📈"
        />
        <ErrorBoundary>
          <WeeklyPerformanceChart />
        </ErrorBoundary>
      </section>

      {/* Section 5: Replenishment Queue */}
      <section id="replenishment" className="mb-12">
        <SectionHeader
          id="replenishment-header"
          title="Replenishment Queue"
          description="Store-level inventory recommendations"
          icon="📦"
        />
        <ErrorBoundary>
          <ReplenishmentQueue />
        </ErrorBoundary>
      </section>

      {/* Section 6: Markdown Decision */}
      <section id="markdown" className="mb-12">
        <SectionHeader
          id="markdown-header"
          title="Markdown Decision"
          description="Clearance strategy optimization"
          icon="💰"
        />
        <ErrorBoundary>
          <MarkdownDecision />
        </ErrorBoundary>
      </section>

      {/* Section 7: Performance Metrics */}
      <section id="performance" className="mb-12">
        <SectionHeader
          id="performance-header"
          title="Performance Metrics"
          description="System accuracy and business impact"
          icon="🎯"
        />
        <ErrorBoundary>
          <PerformanceMetrics />
        </ErrorBoundary>
      </section>

      {/* Upload Modal */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
      />
    </AppLayout>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/reports/:seasonId" element={<ReportPage />} />
    </Routes>
  );
}

export default App;
