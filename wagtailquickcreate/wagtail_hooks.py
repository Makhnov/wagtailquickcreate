from django.apps import apps
from django.conf import settings
from django.urls import path
from django.utils.safestring import mark_safe
from wagtail.admin.site_summary import SiteSummaryPanel, SummaryItem
from wagtail import hooks
from .views import QuickCreateView

class QuickCreatePanel(SummaryItem):
    template_name = "wagtailquickcreate/panel.html"
    order = 50

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        quick_create_page_types = getattr(settings, "WAGTAIL_QUICK_CREATE_PAGE_TYPES", [])
        
        if not quick_create_page_types:
            return ""

        # Make a list of the models with edit links
        # EG [{'link': 'news/NewsPage', 'name': 'News page'}]
        page_models = []
        for path, description in quick_create_page_types:
            item = {}
            # Split the model path and get the model class
            model = apps.get_model(path)
            item['link'] = model._meta.app_label + '/' + model.__name__
            item['name'] = description
            page_models.append(item)

        # Build up an html chunk for the links to be rendered in the panel
        page_models_html_chunk = []
        for item in page_models:
            model = apps.get_model(item['link'].replace('/', '.'))
            # Si le modèle n'a qu'un seul parent, on peut créer une instance de la page directement
            if len(model.parent_page_types) == 1:
                parent_model = apps.get_model(model.parent_page_types[0])
                parent_instance = parent_model.objects.first()  # ou autre logique pour obtenir l'instance parente correcte
                if parent_instance:
                    model_name_lower = model.__name__.lower()
                    link = f"/admin/pages/add/{model._meta.app_label}/{model_name_lower}/{parent_instance.id}/"
                    page_models_html_chunk.append(
                        f'<a href="{link}"><button class="button bicolor button--icon margin-bottom-sm" style="margin-right:6px;margin-bottom:6px;">'
                        f'<span class="icon-wrapper"><svg class="icon icon-plus icon" aria-hidden="true">'
                        f'<use href="#icon-plus"></use></svg></span>Créer {item["name"]}</button></a>'
                    )
                else:
                    pass
            else:
                page_models_html_chunk.append(
                    """
                    <a href="/admin/quickcreate/create/{model_link}/">
                    <button class="button bicolor button--icon margin-bottom-sm" style="margin-right:6px;margin-bottom:6px;">
                    <span class="icon-wrapper">
                    <svg class="icon icon-plus icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                    </span>
                    Créer {model_name}</button></a>""".format(
                        model_link=item['link'], model_name=item['name']
                    )
                )

        page_models = []
        for item in page_models_html_chunk:
            if item not in page_models:                
                page_models.append(item)

        if getattr(settings, "WAGTAIL_QUICK_CREATE_IMAGES", False):
            page_models.append("""
                    <a href="/admin/images/multiple/add/">
                    <button class="button bicolor button--icon" style="margin-right:6px;margin-bottom:6px;">
                    <span class="icon-wrapper">
                    <svg class="icon icon-plus icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                    </span>
                    Ajouter une/des image(s)</button></a>
                    """)
        if getattr(settings, "WAGTAIL_QUICK_CREATE_DOCUMENTS", False):
            page_models.append("""
                    <a href="/admin/documents/multiple/add/">
                    <button class="button bicolor button--icon" style="margin-right:6px;margin-bottom:6px;">
                    <span class="icon-wrapper">
                    <svg class="icon icon-plus icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                    </span>
                    Ajouter un/des document(s)</button></a>
                    """)
        if getattr(settings, "WAGTAIL_QUICK_CREATE_AUDIO", False):
            page_models.append("""
                    <a href="/admin/media/audio/add/">
                    <button class="button bicolor button--icon" style="margin-right:6px;margin-bottom:6px;">
                    <span class="icon-wrapper">
                    <svg class="icon icon-plus icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                    </span>
                    Ajouter un fichier audio</button></a>
                    """)
        if getattr(settings, "WAGTAIL_QUICK_CREATE_VIDEO", False):
            page_models.append("""
                    <a href="/admin/media/video/add/">
                    <button class="button bicolor button--icon" style="margin-right:6px;margin-bottom:6px;">
                    <span class="icon-wrapper">
                    <svg class="icon icon-plus icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                    </span>
                    Ajouter un fichier vidéo</button></a>
                    """)
        context["models"] = mark_safe(''.join(page_models))
        return context


@hooks.register('register_admin_urls')
def urlconf_time():
    # Example: http://127.0.0.1:8000/admin/quickcreate/create/standardpages/InformationPage/
    return [
        path('quickcreate/create/<str:app>/<str:model>/',
            QuickCreateView.as_view()),
    ]


@hooks.register('construct_homepage_panels')
def add_quick_create_panel(request, panels):
    # Replace the site summary panel with our custom panel
    if getattr(settings, "WAGTAIL_QUICK_CREATE_REPLACE_SUMMARY_PANEL", False):
        for i, v in enumerate(panels):
            if isinstance(v, SiteSummaryPanel):
                panels[i] = QuickCreatePanel(request)
    else:
        panels.append(QuickCreatePanel(request))
    return panels
