# myapp/urls.py
from django.urls import path
from .views.home import home, run_evaluation
from .views.dataset import list_datasets, create_dataset, delete_dataset, view_dataset, run_dataset_page
from .views.evaluation import check_processing_status, cancel_processing
from .views.api import api_list_datasets, api_create_dataset, api_dataset_detail, api_delete_dataset

urlpatterns = [
    path('', home, name='home'),
    path('run_evaluation/', run_evaluation, name='run_evaluation'),
    path('datasets/', list_datasets, name='list_datasets'),
    path('datasets/create/', create_dataset, name='create_dataset'),
    path('datasets/delete/<int:dataset_id>/', delete_dataset, name='delete_dataset'),
    path('datasets/view/<int:dataset_id>/', view_dataset, name='view_dataset'),
    path('datasets/run/', run_dataset_page, name='run_dataset_page'),
    path('evaluation/status/', check_processing_status, name='check_processing_status'),
    path('evaluation/cancel/', cancel_processing, name='cancel_processing'),
    # API endpoints for frontend
    path('api/datasets/', api_list_datasets, name='api_list_datasets'),
    path('api/datasets/create/', api_create_dataset, name='api_create_dataset'),
    path('api/datasets/<int:dataset_id>/', api_dataset_detail, name='api_dataset_detail'),
    path('api/datasets/delete/<int:dataset_id>/', api_delete_dataset, name='api_delete_dataset'),
]