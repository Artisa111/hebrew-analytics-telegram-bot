# -*- coding: utf-8 -*-
"""
מודול ניתוח הנתונים - Data analysis module for cleaning, insights, and statistics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_df = df.copy()
        self.insights = {}
        self.analysis_results = {}
    
    def clean_data(self) -> pd.DataFrame:
        """ניקוי וטיפול בנתונים"""
        try:
            # הסרת עמודות ריקות לחלוטין
            self.df = self.df.dropna(how='all', axis=1)
            
            # הסרת שורות ריקות לחלוטין
            self.df = self.df.dropna(how='all', axis=0)
            
            # טיפול בערכים חסרים
            for col in self.df.columns:
                if self.df[col].dtype in ['object', 'string']:
                    # עבור טקסט - מילוי בערך הנפוץ ביותר
                    if self.df[col].isnull().sum() > 0:
                        mode_val = self.df[col].mode().iloc[0] if not self.df[col].mode().empty else "לא ידוע"
                        self.df[col].fillna(mode_val, inplace=True)
                else:
                    # עבור מספרים - מילוי בממוצע או חציון
                    if self.df[col].isnull().sum() > 0:
                        if self.df[col].dtype in ['int64', 'float64']:
                            median_val = self.df[col].median()
                            self.df[col].fillna(median_val, inplace=True)
            
            # הסרת שורות כפולות
            self.df = self.df.drop_duplicates()
            
            # ניקוי שמות עמודות
            self.df.columns = self.df.columns.str.strip().str.replace(' ', '_')
            
            logger.info("Data cleaning completed successfully")
            return self.df
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return self.original_df
    
    def get_basic_info(self) -> Dict[str, Any]:
        """קבלת מידע בסיסי על הנתונים"""
        try:
            info = {
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'data_types': self.df.dtypes.to_dict(),
                'memory_usage': self.df.memory_usage(deep=True).sum(),
                'null_counts': self.df.isnull().sum().to_dict(),
                'duplicate_rows': self.df.duplicated().sum()
            }
            
            # הוספת מידע על עמודות
            column_info = {}
            for col in self.df.columns:
                col_info = {
                    'type': str(self.df[col].dtype),
                    'unique_values': self.df[col].nunique(),
                    'null_count': self.df[col].isnull().sum(),
                    'null_percentage': round((self.df[col].isnull().sum() / len(self.df)) * 100, 2)
                }
                
                if self.df[col].dtype in ['int64', 'float64']:
                    col_info.update({
                        'min': float(self.df[col].min()) if not self.df[col].isnull().all() else None,
                        'max': float(self.df[col].max()) if not self.df[col].isnull().all() else None,
                        'mean': float(self.df[col].mean()) if not self.df[col].isnull().all() else None,
                        'median': float(self.df[col].median()) if not self.df[col].isnull().all() else None,
                        'std': float(self.df[col].std()) if not self.df[col].isnull().all() else None
                    })
                
                column_info[col] = col_info
            
            info['column_details'] = column_info
            self.analysis_results['basic_info'] = info
            return info
            
        except Exception as e:
            logger.error(f"Error getting basic info: {e}")
            return {}
    
    def detect_outliers(self, columns: List[str] = None) -> Dict[str, List[int]]:
        """זיהוי ערכים חריגים בעמודות מספריות"""
        try:
            if columns is None:
                columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            outliers = {}
            for col in columns:
                if col in self.df.columns and self.df[col].dtype in ['int64', 'float64']:
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_indices = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)].index.tolist()
                    outliers[col] = outlier_indices
            
            self.analysis_results['outliers'] = outliers
            return outliers
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return {}
    
    def correlation_analysis(self, method: str = 'pearson') -> pd.DataFrame:
        """ניתוח קורלציה בין עמודות מספריות"""
        try:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                return pd.DataFrame()
            
            correlation_matrix = self.df[numeric_cols].corr(method=method)
            
            # זיהוי קורלציות חזקות
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # קורלציה חזקה
                        strong_correlations.append({
                            'column1': correlation_matrix.columns[i],
                            'column2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            self.analysis_results['correlation_matrix'] = correlation_matrix
            self.analysis_results['strong_correlations'] = strong_correlations
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {e}")
            return pd.DataFrame()
    
    def trend_analysis(self, date_column: str = None, value_column: str = None) -> Dict[str, Any]:
        """ניתוח מגמות לאורך זמן"""
        try:
            trends = {}
            
            # אם יש עמודת תאריך
            if date_column and date_column in self.df.columns:
                try:
                    self.df[date_column] = pd.to_datetime(self.df[date_column], errors='coerce')
                    self.df = self.df.dropna(subset=[date_column])
                    
                    if value_column and value_column in self.df.columns:
                        # ניתוח מגמה פשוט
                        self.df = self.df.sort_values(date_column)
                        
                        # חישוב מגמה לינארית
                        x = np.arange(len(self.df))
                        y = self.df[value_column].values
                        
                        if len(y) > 1:
                            slope = np.polyfit(x, y, 1)[0]
                            trends['slope'] = slope
                            trends['trend_direction'] = 'עולה' if slope > 0 else 'יורדת' if slope < 0 else 'יציבה'
                            trends['trend_strength'] = abs(slope)
                            
                            # זיהוי עונות
                            if len(self.df) > 12:  # מספיק נתונים לניתוח עונתי
                                monthly_avg = self.df.groupby(self.df[date_column].dt.month)[value_column].mean()
                                seasonal_pattern = monthly_avg.to_dict()
                                trends['seasonal_pattern'] = seasonal_pattern
                
                except Exception as e:
                    logger.warning(f"Date trend analysis failed: {e}")
            
            # ניתוח מגמות בעמודות מספריות
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if len(self.df[col].dropna()) > 1:
                    # חישוב שינוי יחסי
                    sorted_values = self.df[col].dropna().sort_values()
                    if len(sorted_values) > 1:
                        relative_change = (sorted_values.iloc[-1] - sorted_values.iloc[0]) / sorted_values.iloc[0]
                        trends[f'{col}_relative_change'] = relative_change
            
            self.analysis_results['trends'] = trends
            return trends
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {}
    
    def segmentation_analysis(self, columns: List[str] = None, n_clusters: int = 3) -> Dict[str, Any]:
        """ניתוח פילוח וקבצים"""
        try:
            if columns is None:
                columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(columns) < 2:
                return {}
            
            # בחירת עמודות לניתוח
            analysis_data = self.df[columns].dropna()
            
            if len(analysis_data) < n_clusters:
                return {}
            
            # נרמול הנתונים
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(analysis_data)
            
            # ניתוח קבצים
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_data)
            
            # ניתוח PCA להפחתת מימדים
            pca = PCA(n_components=2)
            pca_data = pca.fit_transform(scaled_data)
            
            segmentation_results = {
                'clusters': clusters.tolist(),
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'pca_data': pca_data.tolist(),
                'explained_variance': pca.explained_variance_ratio_.tolist(),
                'columns_used': columns
            }
            
            # ניתוח כל קבץ
            cluster_analysis = {}
            for i in range(n_clusters):
                cluster_mask = clusters == i
                cluster_data = analysis_data[cluster_mask]
                
                cluster_analysis[f'cluster_{i}'] = {
                    'size': int(cluster_mask.sum()),
                    'percentage': round((cluster_mask.sum() / len(analysis_data)) * 100, 2),
                    'characteristics': {}
                }
                
                for col in columns:
                    if col in cluster_data.columns:
                        cluster_analysis[f'cluster_{i}']['characteristics'][col] = {
                            'mean': float(cluster_data[col].mean()),
                            'std': float(cluster_data[col].std()),
                            'min': float(cluster_data[col].min()),
                            'max': float(cluster_data[col].max())
                        }
            
            segmentation_results['cluster_analysis'] = cluster_analysis
            self.analysis_results['segmentation'] = segmentation_results
            
            return segmentation_results
            
        except Exception as e:
            logger.error(f"Error in segmentation analysis: {e}")
            return {}
    
    def generate_insights(self) -> List[str]:
        """יצירת תובנות אוטומטיות מהנתונים"""
        try:
            insights = []
            
            # תובנות על גודל הנתונים
            rows, cols = self.df.shape
            insights.append(f"הנתונים מכילים {rows:,} שורות ו-{cols} עמודות")
            
            # תובנות על ערכים חסרים
            total_cells = rows * cols
            missing_cells = self.df.isnull().sum().sum()
            if missing_cells > 0:
                missing_percentage = round((missing_cells / total_cells) * 100, 2)
                insights.append(f"יש {missing_cells:,} ערכים חסרים ({missing_percentage}% מהנתונים)")
            
            # תובנות על כפילויות
            if 'duplicate_rows' in self.analysis_results.get('basic_info', {}):
                dup_count = self.analysis_results['basic_info']['duplicate_rows']
                if dup_count > 0:
                    insights.append(f"נמצאו {dup_count} שורות כפולות")
            
            # תובנות על ערכים חריגים
            if 'outliers' in self.analysis_results:
                total_outliers = sum(len(indices) for indices in self.analysis_results['outliers'].values())
                if total_outliers > 0:
                    insights.append(f"זוהו {total_outliers} ערכים חריגים בעמודות מספריות")
            
            # תובנות על קורלציות
            if 'strong_correlations' in self.analysis_results:
                strong_corr_count = len(self.analysis_results['strong_correlations'])
                if strong_corr_count > 0:
                    insights.append(f"נמצאו {strong_corr_count} קורלציות חזקות בין עמודות")
            
            # תובנות על מגמות
            if 'trends' in self.analysis_results:
                trends = self.analysis_results['trends']
                if 'trend_direction' in trends:
                    insights.append(f"המגמה הכללית היא {trends['trend_direction']}")
            
            # תובנות על פילוח
            if 'segmentation' in self.analysis_results:
                seg = self.analysis_results['segmentation']
                if 'cluster_analysis' in seg:
                    largest_cluster = max(seg['cluster_analysis'].values(), key=lambda x: x['size'])
                    insights.append(f"הקבץ הגדול ביותר מכיל {largest_cluster['size']} רשומות ({largest_cluster['percentage']}%)")
            
            # תובנות על עמודות
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                insights.append(f"יש {len(numeric_cols)} עמודות מספריות לניתוח כמותי")
            
            text_cols = self.df.select_dtypes(include=['object', 'string']).columns
            if len(text_cols) > 0:
                insights.append(f"יש {len(text_cols)} עמודות טקסט לניתוח איכותני")
            
            self.insights = insights
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["לא ניתן ליצור תובנות בשל שגיאה בניתוח"]
    
    def answer_natural_language_question(self, question: str) -> str:
        """מענה על שאלות בשפה טבעית בעברית"""
        try:
            question_lower = question.lower()
            
            # שאלות על סטטיסטיקות בסיסיות
            if any(word in question_lower for word in ['ממוצע', 'ממוצעים', 'ממוצע של']):
                for col in self.df.select_dtypes(include=[np.number]).columns:
                    if col in question_lower:
                        mean_val = self.df[col].mean()
                        return f"הממוצע של {col} הוא {mean_val:.2f}"
            
            if any(word in question_lower for word in ['סכום', 'סה"כ', 'סה"כ של']):
                for col in self.df.select_dtypes(include=[np.number]).columns:
                    if col in question_lower:
                        sum_val = self.df[col].sum()
                        return f"הסכום של {col} הוא {sum_val:,.2f}"
            
            # שאלות על ערכים מקסימליים ומינימליים
            if any(word in question_lower for word in ['הכי הרבה', 'הכי גדול', 'הכי גבוה', 'מקסימום']):
                for col in self.df.select_dtypes(include=[np.number]).columns:
                    if col in question_lower:
                        max_val = self.df[col].max()
                        max_idx = self.df[col].idxmax()
                        return f"הערך הגבוה ביותר ב-{col} הוא {max_val:.2f}"
            
            if any(word in question_lower for word in ['הכי מעט', 'הכי קטן', 'הכי נמוך', 'מינימום']):
                for col in self.df.select_dtypes(include=[np.number]).columns:
                    if col in question_lower:
                        min_val = self.df[col].min()
                        min_idx = self.df[col].idxmin()
                        return f"הערך הנמוך ביותר ב-{col} הוא {min_val:.2f}"
            
            # שאלות על גודל הנתונים
            if any(word in question_lower for word in ['כמה', 'גודל', 'מספר']):
                if 'שורות' in question_lower or 'רשומות' in question_lower:
                    return f"יש {len(self.df):,} שורות בנתונים"
                elif 'עמודות' in question_lower or 'עמודות' in question_lower:
                    return f"יש {len(self.df.columns)} עמודות בנתונים"
            
            # שאלות על מגמות
            if any(word in question_lower for word in ['מגמה', 'טרנד', 'כיוון']):
                if 'trends' in self.analysis_results:
                    trends = self.analysis_results['trends']
                    if 'trend_direction' in trends:
                        return f"המגמה הכללית היא {trends['trend_direction']}"
            
            # שאלה כללית
            return "אני לא מבין את השאלה. אנא נסה לשאול בצורה אחרת או בחר מהאפשרויות המוצעות."
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "שגיאה במענה על השאלה. אנא נסה שוב."
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """קבלת סיכום מלא של הניתוח"""
        try:
            summary = {
                'basic_info': self.get_basic_info(),
                'outliers': self.detect_outliers(),
                'correlation': self.correlation_analysis(),
                'trends': self.trend_analysis(),
                'segmentation': self.segmentation_analysis(),
                'insights': self.generate_insights()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting analysis summary: {e}")
            return {}

