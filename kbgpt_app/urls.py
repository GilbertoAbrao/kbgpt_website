from django.urls import path

from .views import upload_file_view, login_page_view, MainTemplateView, register_view, \
chatbot_create_view, chatbot_list_view, chatbot_update_view, chatbot_delete_view, chatbot_document_create_view, \
qa_view, chatbot_document_webhook_view

urlpatterns = [

    path('file/', upload_file_view, name='upload_file'),
    path('', login_page_view, name='login'),
    path('register/', register_view, name='register'),
    path('main/', MainTemplateView.as_view(), name='main'),

    # CRUD Bot -----------------------------------------------------------------------
    path('chatbots/', chatbot_list_view, name='chatbot_list_url'),
    path('chatbot/', chatbot_create_view, name='chatbot_create_url'),
    path('chatbot/<pk>/', chatbot_update_view, name='chatbot_update_url'),
    path('chatbot/<pk>/delete/', chatbot_delete_view, name='chatbot_delete_url'),
    path('chatbot/<pk>/document/', chatbot_document_create_view, name='chatbot_document_create_url'),
    path('chatbot/<pk>/document/<uuid>/webhook/', chatbot_document_webhook_view, name='chatbot_document_webhook_url'),
    
    # QA -----------------------------------------------------------------------------
    path('qa/', qa_view, name='qa_url'),

]