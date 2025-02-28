# -*- coding: utf-8 -*-
"""scoutium.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aRHbMvebb_G6nqY0K9ZtLnPUKM7HM5wT
"""

import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import GridSearchCV, cross_validate, RandomizedSearchCV, validation_curve
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
warnings.simplefilter(action='ignore', category=Warning)

df_attributes = pd.read_csv("/content/drive/MyDrive/Datasets/scoutium_attributes.csv", sep=";")
df_labels = pd.read_csv("/content/drive/MyDrive/Datasets/scoutium_potential_labels.csv", sep=";")

print("Columns in df_attributes:", df_attributes.columns)
print("Columns in df_labels:", df_labels.columns)
# Sütunlara " , " ile değil " ; " ile ayrılmış . Buyüzden " sep=";" " komutuyla veri setini okuyoruz.

df_merged = pd.merge(df_attributes, df_labels, on=["task_response_id", "match_id", "evaluator_id", "player_id"])

df_merged.head(20)

df_merged.info()

df_merged.describe().T

df_merged = df_merged[df_merged["position_id"] != 1]
print(df_merged["position_id"].unique())  # İçinde 1 olup olmadığını kontrol ederiz

print(df_merged["potential_label"].value_counts())

# ( below_average sınıfı tüm verisetinin %1'ini oluşturur) bu yüzden veri setinden kaldıracağız.

df_merged = df_merged[df_merged["potential_label"] != "below_average"]
print(df_merged["potential_label"].unique())  # "below_average" olup olmadığını kontrol ederiz

'''Adım5: Oluşturduğunuz veri setinden “pivot_table” fonksiyonunu kullanarak bir tablo oluşturunuz. Bu pivot table'da her satırda bir oyuncu
olacak şekilde manipülasyon yapınız.
Görevler
Adım5.1: İndekste “player_id”,“position_id” ve “potential_label”, sütunlarda “attribute_id” ve değerlerde scout’ların oyunculara verdiği puan
“attribute_value” olacak şekilde pivot table’ı oluşturunuz.
Adım5.2: “reset_index” fonksiyonunu kullanarak indeksleri değişken olarak atayınız ve “attribute_id” sütunlarının isimlerini stringe çeviriniz.
'''

df_pivot = df_merged.pivot_table(
    index=["player_id", "position_id", "potential_label"],  # Satırlardaki değişkenler
    columns="attribute_id",  # Sütun olarak attribute_id
    values="attribute_value",  # Değer olarak attribute_value
    aggfunc="mean"  # Eğer aynı oyuncuya birden fazla değer varsa ortalamasını alır
)

df_pivot = df_pivot.reset_index()

df_pivot.columns = df_pivot.columns.astype(str)

df_pivot.head()

from sklearn.preprocessing import LabelEncoder

# LabelEncoder'ı başlatıyoruz
label_encoder = LabelEncoder()

# 'potential_label' sütununu sayısal değerlere dönüştürüyoruz
df_merged["potential_label_encoded"] = label_encoder.fit_transform(df_merged["potential_label"])

# Sonuç olarak yeni sütun eklenmiş olacak
print(df_merged[["potential_label", "potential_label_encoded"]].head())

# Sayısal veri tipindeki sütunları seçiyoruz
num_cols = df_merged.select_dtypes(include=["number"]).columns.tolist()

num_cols.remove("potential_label_encoded")  # ölçeklenecek sütunlar listesinden kodlanmış etiketi çıkar

# 'num_cols' listesini görüntülüyoruz
print(num_cols)

from sklearn.preprocessing import StandardScaler

# StandardScaler'ı başlatıyoruz
scaler = StandardScaler()

# Sayısal sütunları seçip ölçeklendiriyoruz
df_merged[num_cols] = scaler.fit_transform(df_merged[num_cols])

# Ölçeklendirilmiş veriyi kontrol ediyoruz
print(df_merged[num_cols].head())

from sklearn.model_selection import train_test_split

# Özellikler (features) ve hedef değişkeni (target) ayırıyoruz
X = df_merged[num_cols]  # Özellikler
y = df_merged["potential_label_encoded"]  # Hedef değişken

# Eğer hedef değişken sürekli bir değer ise, kategorik hale getirelim (örn. 0 ve 1 gibi)
y_train = y_train.astype(int)
y_test = y_test.astype(int)

# Veriyi eğitim ve test olarak ayırıyoruz (test oranı %20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 'potential_label' sütununu sayısal değerlere dönüştürüyoruz for the training and test sets seperately
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

# Regresyon modeli için LightGBM Regressor
from lightgbm import LGBMClassifier # Changed from LGBMRegressor

# Modeli oluşturuyoruz
model = LGBMClassifier() # Changed from LGBMRegressor

# Modeli eğitiyoruz
model.fit(X_train, y_train_encoded) # Use the encoded target for training

# Test verisi üzerinde tahmin yapıyoruz
y_pred = model.predict(X_test)

# Sonuçları kontrol edebilirsiniz
print(y_pred)

from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Tahminler
y_pred = model.predict(X_test)

# Metrikleri hesaplıyoruz
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

# Sonuçları yazdırıyoruz
print(f"R² (R-kare): {r2:.4f}")
print(f"MSE (Mean Squared Error): {mse:.4f}")
print(f"RMSE (Root Mean Squared Error): {rmse:.4f}")

from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, accuracy_score

# Tahminler
y_pred_class = model.predict(X_test)

# Metrikleri hesaplıyoruz
roc_auc = roc_auc_score(y_test, y_pred_class)
f1 = f1_score(y_test, y_pred_class)
precision = precision_score(y_test, y_pred_class)
recall = recall_score(y_test, y_pred_class)
accuracy = accuracy_score(y_test, y_pred_class)

# Sonuçları yazdırıyoruz
print(f"ROC AUC: {roc_auc:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"Accuracy: {accuracy:.4f}")

#Feature İmportance Visualization

def plot_importance(model, features, num=len(X), save=False) :
    feature_imp = pd.DataFrame ( {'Value' : model.feature_importances_, 'Feature' : features.columns})
    plt.figure(figsize=(10, 10))
    sns.set(font_scale=1)
    sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value",
                                                                    ascending=False) [0: num])
    plt.title ( 'Features' )
    plt.tight_layout ()
    plt.show ()
    if save:
        plt.savefig('importances.png')

plot_importance(model, X)