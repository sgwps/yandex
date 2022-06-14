"""goodsapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from logging import getLogRecordFactory
from django.contrib import admin
from django.urls import path
import goods.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('imports', goods.views.Imports.as_view()),
    path('delete/<str:id>', goods.views.Delete.as_view()),
    path('nodes/<str:id>', goods.views.Nodes.as_view()),
    path('delete', goods.views.DeleteEmpty.as_view()),
    path('nodes', goods.views.NodesEmpty.as_view()),
    path('sales', goods.views.Sales.as_view()),
    path('node/<str:id>/statistic', goods.views.NodeStatistic.as_view())
]
