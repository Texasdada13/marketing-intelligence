"""File Analyzer for CSV/Excel Data Analysis"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import io
import csv


@dataclass
class ColumnAnalysis:
    """Analysis of a single column."""
    name: str
    dtype: str  # 'numeric', 'text', 'date', 'boolean'
    sample_values: List[Any]
    unique_count: int
    null_count: int
    min_value: Any = None
    max_value: Any = None
    mean_value: float = None


@dataclass
class FileAnalysisResult:
    """Result of file analysis."""
    filename: str
    file_type: str
    row_count: int
    column_count: int
    columns: List[ColumnAnalysis]
    data_summary: str
    sample_rows: List[Dict[str, Any]]
    detected_metrics: Dict[str, Any]
    context_json: Dict[str, Any]
    insights: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'file_type': self.file_type,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'columns': [
                {
                    'name': c.name,
                    'dtype': c.dtype,
                    'sample_values': c.sample_values[:3],
                    'unique_count': c.unique_count,
                    'null_count': c.null_count
                }
                for c in self.columns
            ],
            'data_summary': self.data_summary,
            'sample_rows': self.sample_rows[:5],
            'detected_metrics': self.detected_metrics,
            'insights': self.insights
        }


class FileAnalyzer:
    """Analyzes uploaded CSV/Excel files for chat context."""

    SUPPORTED_FORMATS = ['csv', 'tsv', 'json']
    MAX_ROWS = 1000
    MAX_SAMPLE_ROWS = 10

    # Marketing-specific metric patterns
    MARKETING_METRIC_PATTERNS = {
        'revenue': ['revenue', 'sales', 'income', 'earnings'],
        'cost': ['cost', 'spend', 'expense', 'budget', 'investment'],
        'clicks': ['click', 'clicks', 'ctr'],
        'impressions': ['impression', 'impressions', 'reach', 'views'],
        'conversions': ['conversion', 'conversions', 'leads', 'signups'],
        'roi': ['roi', 'roas', 'return'],
        'cac': ['cac', 'acquisition cost', 'cpa', 'cost per'],
        'engagement': ['engagement', 'likes', 'shares', 'comments'],
        'campaign': ['campaign', 'ad', 'creative'],
        'channel': ['channel', 'source', 'medium', 'platform'],
    }

    def __init__(self):
        pass

    def analyze_file(self, content: bytes, filename: str) -> FileAnalysisResult:
        """Analyze an uploaded file and return analysis result."""
        file_type = self._detect_file_type(filename)

        if file_type == 'csv':
            return self._analyze_csv(content, filename)
        elif file_type == 'tsv':
            return self._analyze_csv(content, filename, delimiter='\t')
        elif file_type == 'json':
            return self._analyze_json(content, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _detect_file_type(self, filename: str) -> str:
        """Detect file type from filename."""
        lower_name = filename.lower()
        if lower_name.endswith('.csv'):
            return 'csv'
        elif lower_name.endswith('.tsv'):
            return 'tsv'
        elif lower_name.endswith('.json'):
            return 'json'
        else:
            # Default to CSV
            return 'csv'

    def _analyze_csv(self, content: bytes, filename: str, delimiter: str = ',') -> FileAnalysisResult:
        """Analyze a CSV file."""
        try:
            # Decode content
            text = content.decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            text = content.decode('latin-1')

        # Parse CSV
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        rows = []
        for i, row in enumerate(reader):
            if i >= self.MAX_ROWS:
                break
            rows.append(row)

        if not rows:
            return self._create_empty_result(filename, 'csv')

        # Analyze columns
        columns = self._analyze_columns(rows)

        # Detect metrics
        detected_metrics = self._detect_marketing_metrics(columns, rows)

        # Generate insights
        insights = self._generate_insights(columns, rows, detected_metrics)

        # Create summary
        summary = self._create_summary(filename, rows, columns, detected_metrics)

        # Build context for AI
        context_json = self._build_context_json(columns, rows, detected_metrics)

        return FileAnalysisResult(
            filename=filename,
            file_type='csv',
            row_count=len(rows),
            column_count=len(columns),
            columns=columns,
            data_summary=summary,
            sample_rows=rows[:self.MAX_SAMPLE_ROWS],
            detected_metrics=detected_metrics,
            context_json=context_json,
            insights=insights
        )

    def _analyze_json(self, content: bytes, filename: str) -> FileAnalysisResult:
        """Analyze a JSON file."""
        data = json.loads(content.decode('utf-8'))

        # Handle different JSON structures
        if isinstance(data, list):
            rows = data[:self.MAX_ROWS]
        elif isinstance(data, dict):
            # Try common patterns
            if 'data' in data:
                rows = data['data'][:self.MAX_ROWS]
            elif 'results' in data:
                rows = data['results'][:self.MAX_ROWS]
            elif 'rows' in data:
                rows = data['rows'][:self.MAX_ROWS]
            else:
                # Treat as single record
                rows = [data]
        else:
            rows = []

        if not rows or not isinstance(rows[0], dict):
            return self._create_empty_result(filename, 'json')

        columns = self._analyze_columns(rows)
        detected_metrics = self._detect_marketing_metrics(columns, rows)
        insights = self._generate_insights(columns, rows, detected_metrics)
        summary = self._create_summary(filename, rows, columns, detected_metrics)
        context_json = self._build_context_json(columns, rows, detected_metrics)

        return FileAnalysisResult(
            filename=filename,
            file_type='json',
            row_count=len(rows),
            column_count=len(columns),
            columns=columns,
            data_summary=summary,
            sample_rows=rows[:self.MAX_SAMPLE_ROWS],
            detected_metrics=detected_metrics,
            context_json=context_json,
            insights=insights
        )

    def _analyze_columns(self, rows: List[Dict[str, Any]]) -> List[ColumnAnalysis]:
        """Analyze each column in the data."""
        if not rows:
            return []

        columns = []
        all_keys = set()
        for row in rows:
            all_keys.update(row.keys())

        for key in all_keys:
            values = [row.get(key) for row in rows]
            non_null_values = [v for v in values if v is not None and v != '']

            # Determine type
            dtype = self._infer_dtype(non_null_values)

            # Calculate stats
            unique_count = len(set(str(v) for v in non_null_values))
            null_count = len(values) - len(non_null_values)

            col = ColumnAnalysis(
                name=key,
                dtype=dtype,
                sample_values=non_null_values[:5],
                unique_count=unique_count,
                null_count=null_count
            )

            # Add numeric stats
            if dtype == 'numeric' and non_null_values:
                try:
                    numeric_vals = [float(v) for v in non_null_values]
                    col.min_value = min(numeric_vals)
                    col.max_value = max(numeric_vals)
                    col.mean_value = sum(numeric_vals) / len(numeric_vals)
                except (ValueError, TypeError):
                    pass

            columns.append(col)

        return columns

    def _infer_dtype(self, values: List[Any]) -> str:
        """Infer data type from values."""
        if not values:
            return 'text'

        # Check for numeric
        numeric_count = 0
        for v in values[:20]:  # Sample first 20
            try:
                float(str(v).replace(',', '').replace('$', '').replace('%', ''))
                numeric_count += 1
            except (ValueError, TypeError):
                pass

        if numeric_count > len(values[:20]) * 0.8:
            return 'numeric'

        # Check for boolean
        bool_values = {'true', 'false', 'yes', 'no', '1', '0'}
        if all(str(v).lower() in bool_values for v in values[:20]):
            return 'boolean'

        return 'text'

    def _detect_marketing_metrics(
        self,
        columns: List[ColumnAnalysis],
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect marketing-related metrics in the data."""
        detected = {}

        for col in columns:
            col_lower = col.name.lower()

            for metric_type, patterns in self.MARKETING_METRIC_PATTERNS.items():
                if any(p in col_lower for p in patterns):
                    if col.dtype == 'numeric' and col.mean_value is not None:
                        detected[metric_type] = {
                            'column': col.name,
                            'mean': round(col.mean_value, 2),
                            'min': col.min_value,
                            'max': col.max_value
                        }
                    else:
                        detected[metric_type] = {
                            'column': col.name,
                            'unique_values': col.unique_count
                        }
                    break

        return detected

    def _generate_insights(
        self,
        columns: List[ColumnAnalysis],
        rows: List[Dict[str, Any]],
        detected_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from the data."""
        insights = []

        # Data size insight
        insights.append(f"Dataset contains {len(rows)} rows and {len(columns)} columns.")

        # Detected metrics insight
        if detected_metrics:
            metric_names = list(detected_metrics.keys())
            insights.append(f"Detected marketing metrics: {', '.join(metric_names)}")

        # Numeric column insights
        numeric_cols = [c for c in columns if c.dtype == 'numeric' and c.mean_value]
        for col in numeric_cols[:3]:
            if col.mean_value is not None:
                insights.append(
                    f"{col.name}: avg={col.mean_value:.2f}, range={col.min_value:.2f}-{col.max_value:.2f}"
                )

        # High cardinality warning
        high_cardinality = [c for c in columns if c.unique_count > len(rows) * 0.9 and c.dtype == 'text']
        if high_cardinality:
            insights.append(
                f"High cardinality columns (likely IDs): {', '.join(c.name for c in high_cardinality[:3])}"
            )

        return insights[:10]

    def _create_summary(
        self,
        filename: str,
        rows: List[Dict[str, Any]],
        columns: List[ColumnAnalysis],
        detected_metrics: Dict[str, Any]
    ) -> str:
        """Create a text summary of the data."""
        parts = [f"File: {filename}", f"Rows: {len(rows)}, Columns: {len(columns)}"]

        if detected_metrics:
            parts.append(f"Detected metrics: {', '.join(detected_metrics.keys())}")

        # Add column summary
        col_types = {}
        for col in columns:
            col_types[col.dtype] = col_types.get(col.dtype, 0) + 1
        type_summary = ', '.join(f"{v} {k}" for k, v in col_types.items())
        parts.append(f"Column types: {type_summary}")

        return " | ".join(parts)

    def _build_context_json(
        self,
        columns: List[ColumnAnalysis],
        rows: List[Dict[str, Any]],
        detected_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context JSON for AI prompts."""
        return {
            'schema': [
                {
                    'name': c.name,
                    'type': c.dtype,
                    'sample': c.sample_values[:2]
                }
                for c in columns
            ],
            'metrics': detected_metrics,
            'sample_data': rows[:3],
            'row_count': len(rows)
        }

    def _create_empty_result(self, filename: str, file_type: str) -> FileAnalysisResult:
        """Create an empty result for files with no data."""
        return FileAnalysisResult(
            filename=filename,
            file_type=file_type,
            row_count=0,
            column_count=0,
            columns=[],
            data_summary="No data found in file",
            sample_rows=[],
            detected_metrics={},
            context_json={},
            insights=["File appears to be empty or has no recognizable data structure"]
        )


# Factory function
def create_file_analyzer() -> FileAnalyzer:
    return FileAnalyzer()
