"""
Machine Learning Models Module
Implements Regression, Classification, Clustering, and Deep Learning
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error,
                             classification_report, confusion_matrix, accuracy_score,
                             silhouette_score, davies_bouldin_score)
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
import xgboost as xgb
import lightgbm as lgb
import pickle
import warnings
warnings.filterwarnings('ignore')

class CrimeMLModels:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.results = {}
        
    # ============ REGRESSION MODELS ============
    def train_regression_models(self, X_train, X_test, y_train, y_test, problem_name="regression"):
        """Train multiple regression models and compare performance"""
        print(f"\n{'='*60}")
        print(f"REGRESSION: {problem_name}")
        print(f"{'='*60}")
        
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=1.0),
            'Decision Tree': DecisionTreeRegressor(max_depth=10, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, max_depth=5, random_state=42),
            'LightGBM': lgb.LGBMRegressor(n_estimators=100, max_depth=5, random_state=42, verbose=-1)
        }
        
        results = {}
        best_score = -np.inf
        best_model_name = None
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            results[name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'predictions': y_pred_test
            }
            
            print(f"  Train R²: {train_r2:.4f} | Test R²: {test_r2:.4f}")
            print(f"  Train RMSE: {train_rmse:.2f} | Test RMSE: {test_rmse:.2f}")
            print(f"  Train MAE: {train_mae:.2f} | Test MAE: {test_mae:.2f}")
            
            if test_r2 > best_score:
                best_score = test_r2
                best_model_name = name
        
        print(f"\n🏆 Best Model: {best_model_name} (R² = {best_score:.4f})")
        
        self.results[problem_name] = results
        return results, best_model_name
    
    # ============ CLASSIFICATION MODELS ============
    def train_classification_models(self, X_train, X_test, y_train, y_test, problem_name="classification"):
        """Train multiple classification models"""
        print(f"\n{'='*60}")
        print(f"CLASSIFICATION: {problem_name}")
        print(f"{'='*60}")
        
        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            'XGBoost': xgb.XGBClassifier(n_estimators=100, max_depth=5, random_state=42, eval_metric='logloss'),
            'LightGBM': lgb.LGBMClassifier(n_estimators=100, max_depth=5, random_state=42, verbose=-1)
        }
        
        results = {}
        best_score = -np.inf
        best_model_name = None
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Metrics
            train_acc = accuracy_score(y_train, y_pred_train)
            test_acc = accuracy_score(y_test, y_pred_test)
            
            results[name] = {
                'model': model,
                'train_accuracy': train_acc,
                'test_accuracy': test_acc,
                'predictions': y_pred_test,
                'classification_report': classification_report(y_test, y_pred_test, output_dict=True),
                'confusion_matrix': confusion_matrix(y_test, y_pred_test)
            }
            
            print(f"  Train Accuracy: {train_acc:.4f} | Test Accuracy: {test_acc:.4f}")
            
            if test_acc > best_score:
                best_score = test_acc
                best_model_name = name
        
        print(f"\n🏆 Best Model: {best_model_name} (Accuracy = {best_score:.4f})")
        
        self.results[problem_name] = results
        return results, best_model_name
    
    # ============ CLUSTERING MODELS ============
    def train_clustering_models(self, X, problem_name="clustering", n_clusters=5):
        """Train multiple clustering models"""
        print(f"\n{'='*60}")
        print(f"CLUSTERING: {problem_name}")
        print(f"{'='*60}")
        
        # Scale features for clustering
        X_scaled = self.scaler.fit_transform(X)
        
        models = {
            'KMeans': KMeans(n_clusters=n_clusters, random_state=42, n_init=10),
            'Agglomerative': AgglomerativeClustering(n_clusters=n_clusters),
        }
        
        results = {}
        best_score = -np.inf
        best_model_name = None
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            labels = model.fit_predict(X_scaled)
            
            # Metrics
            silhouette = silhouette_score(X_scaled, labels)
            davies_bouldin = davies_bouldin_score(X_scaled, labels)
            
            results[name] = {
                'model': model,
                'labels': labels,
                'silhouette_score': silhouette,
                'davies_bouldin_score': davies_bouldin,
                'n_clusters': n_clusters
            }
            
            print(f"  Silhouette Score: {silhouette:.4f}")
            print(f"  Davies-Bouldin Score: {davies_bouldin:.4f}")
            print(f"  Cluster Distribution: {np.bincount(labels)}")
            
            if silhouette > best_score:
                best_score = silhouette
                best_model_name = name
        
        print(f"\n🏆 Best Model: {best_model_name} (Silhouette = {best_score:.4f})")
        
        self.results[problem_name] = results
        return results, best_model_name
    
    # ============ DIMENSIONALITY REDUCTION ============
    def apply_pca(self, X, n_components=10):
        """Apply PCA for dimensionality reduction"""
        print(f"\nApplying PCA (n_components={n_components})...")
        X_scaled = self.scaler.fit_transform(X)
        
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        
        variance_ratio = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(variance_ratio)
        
        print(f"Explained Variance Ratio: {variance_ratio[:5]}")
        print(f"Cumulative Variance (first 5): {cumulative_variance[:5]}")
        print(f"Total Variance Explained: {cumulative_variance[-1]:.4f}")
        
        return X_pca, pca, variance_ratio, cumulative_variance
    
    def save_model(self, model, filename):
        """Save model to disk"""
        with open(filename, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to {filename}")
    
    def load_model(self, filename):
        """Load model from disk"""
        with open(filename, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {filename}")
        return model

if __name__ == "__main__":
    from data_preprocessing import CrimeDataPreprocessor
    
    print("Loading and preprocessing data...")
    processor = CrimeDataPreprocessor()
    missing_df, crimes_df = processor.load_data()
    missing_clean = processor.clean_missing_persons(missing_df)
    crimes_clean = processor.clean_juvenile_crimes(crimes_df)
    
    # Initialize ML models
    ml = CrimeMLModels()
    
    # Test 1: Regression - Predict total missing persons
    print("\n" + "="*80)
    print("TEST 1: REGRESSION - Predicting Total Missing Persons")
    print("="*80)
    
    X, y, feature_cols = processor.prepare_for_modeling(missing_clean, 'total_missing')
    X = X[[col for col in X.columns if col not in ['male_total', 'female_total', 
                                                     'transgender_total', 'children_missing',
                                                     'youth_missing', 'adults_missing', 
                                                     'elderly_missing']]]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    reg_results, best_reg = ml.train_regression_models(X_train, X_test, y_train, y_test, 
                                                        "Predicting_Missing_Persons")
    
    # Test 2: Classification - High vs Low Crime Districts
    print("\n" + "="*80)
    print("TEST 2: CLASSIFICATION - High vs Low Crime Districts")
    print("="*80)
    
    crimes_for_class = crimes_clean.copy()
    crime_threshold = crimes_for_class['total_crimes'].median()
    crimes_for_class['crime_level'] = (crimes_for_class['total_crimes'] > crime_threshold).astype(int)
    
    X_class, y_class, _ = processor.prepare_for_modeling(crimes_for_class, 'crime_level')
    X_class = X_class[[col for col in X_class.columns if col not in ['total_crimes', 
                                                                       'violent_crimes',
                                                                       'sexual_crimes',
                                                                       'property_crimes']]][:50]
    
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_class, y_class, 
                                                                  test_size=0.2, random_state=42)
    class_results, best_class = ml.train_classification_models(X_train_c, X_test_c, 
                                                                y_train_c, y_test_c,
                                                                "Crime_Level_Classification")
    
    # Test 3: Clustering - State-level patterns
    print("\n" + "="*80)
    print("TEST 3: CLUSTERING - State-level Crime Patterns")
    print("="*80)
    
    state_agg = processor.get_state_aggregated(crimes_clean)
    clustering_features = ['total_crimes', 'violent_crimes', 'sexual_crimes', 'property_crimes']
    X_cluster = state_agg[clustering_features]
    
    cluster_results, best_cluster = ml.train_clustering_models(X_cluster, 
                                                                "State_Crime_Patterns",
                                                                n_clusters=5)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
