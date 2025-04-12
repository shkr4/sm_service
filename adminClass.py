from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin import AdminIndexView, expose


class MyAdminHome(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class adminsAdmin(SecureModelView):
    can_create = True
    column_list = ['ID', 'name', 'username',
                   'password',]  # Show relevant columns
    form_columns = ['name', 'username', 'password',]  # Fields in the form


class customersAdmin(SecureModelView):
    can_create = True
    column_list = ['ID', 'name', 'address', 'ph', 'email', 'created_at']
    form_columns = ['name', 'address', 'ph', 'email']


class paymentAdmin(SecureModelView):
    can_create = True
    column_list = ['ID', 'customer_id', 'amount',
                   'comment', 'status', 'created_at']
    form_columns = ['customer_id', 'amount', 'comment', 'status']

    column_searchable_list = [
        'status']

    # 🔽 Filters
    column_filters = [
        'status',
        'amount'
    ]
