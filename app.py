import os
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from queries import (
    get_kpi_summary,
    get_monthly_revenue,
    get_top_categories,
    get_order_status,
    get_payment_methods,
    get_orders_by_state,
    get_avg_delivery_time,
    get_daily_orders,
    get_new_customers_monthly,
    get_revenue_vs_freight
)

# ── App init ───────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Olist Sales Dashboard"
)
server = app.server  # For deployment

# ── Load all data once at startup ──────────────────────────────────
print("Loading data from PostgreSQL...")
kpi          = get_kpi_summary().iloc[0]
df_revenue   = get_monthly_revenue()
df_cats      = get_top_categories()
df_status    = get_order_status()
df_payments  = get_payment_methods()
df_states    = get_orders_by_state()
df_delivery  = get_avg_delivery_time()
df_daily     = get_daily_orders()
df_new_cust  = get_new_customers_monthly()
df_freight   = get_revenue_vs_freight()
print("All data loaded ✅")

# ── Color palette ──────────────────────────────────────────────────
COLORS = {
    'bg':       '#1a1a2e',
    'card':     '#16213e',
    'accent':   '#0f3460',
    'green':    '#00d4aa',
    'blue':     '#4fc3f7',
    'orange':   '#ff7043',
    'purple':   '#ce93d8',
    'text':     '#ffffff',
    'subtext':  '#b0bec5',
}

# ── Build all charts ───────────────────────────────────────────────

# 1. Monthly Revenue Line Chart
fig_revenue = px.line(
    df_revenue, x='month', y='revenue',
    title='Monthly Revenue Trend',
    color_discrete_sequence=[COLORS['green']]
)
fig_revenue.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    xaxis_title='Month',
    yaxis_title='Revenue (R$)',
    hovermode='x unified'
)
fig_revenue.update_traces(line_width=2.5, fill='tozeroy', fillcolor='rgba(0,212,170,0.1)')

# 2. Top Categories Bar Chart
fig_cats = px.bar(
    df_cats.sort_values('revenue'),
    x='revenue', y='category',
    orientation='h',
    title='Top 10 Categories by Revenue',
    color='revenue',
    color_continuous_scale='Teal',
    text='revenue'
)
fig_cats.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    showlegend=False,
    coloraxis_showscale=False,
    yaxis_title='',
    xaxis_title='Revenue (R$)',
    margin=dict(l=180),
    yaxis=dict(tickfont=dict(size=11))
)
fig_cats.update_traces(texttemplate='R$%{text:,.0f}', textposition='outside')

# 3. Order Status Donut Chart - Simplified to delivered vs rest
df_status_simple = df_status.copy()
df_status_simple['order_status'] = df_status_simple['order_status'].apply(
    lambda x: 'Delivered' if x == 'delivered' else 'Other'
)
df_status_simple = df_status_simple.groupby('order_status')['total_orders'].sum().reset_index()

fig_status = px.pie(
    df_status_simple,
    values='total_orders',
    names='order_status',
    title='Delivered vs Other Orders',
    hole=0.6,
    color_discrete_sequence=[COLORS['green'], COLORS['accent']]
)
fig_status.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16
)
fig_status.update_traces(
    textinfo='percent+label',
    textfont_size=14
)

# 4. Payment Methods Bar Chart
fig_payments = px.bar(
    df_payments, x='payment_type', y='total_revenue',
    title='Revenue by Payment Method',
    color='payment_type',
    color_discrete_sequence=[COLORS['blue'], COLORS['green'],
                              COLORS['orange'], COLORS['purple'], '#ef5350'],
    text='total_revenue'
)
fig_payments.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    showlegend=False,
    xaxis_title='Payment Type',
    yaxis_title='Total Revenue (R$)'
)
fig_payments.update_traces(texttemplate='R$%{text:,.0f}', textposition='outside')

# 5. Orders by State Bar Chart
fig_states = px.bar(
    df_states.sort_values('total_orders'),
    x='total_orders', y='state',
    orientation='h',
    title='Top 10 States by Orders',
    color='total_orders',
    color_continuous_scale='Blues',
)
fig_states.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    coloraxis_showscale=False,
    yaxis_title='',
    xaxis_title='Total Orders'
)

# 6. Avg Delivery Time Bar Chart
fig_delivery = px.bar(
    df_delivery.sort_values('avg_delivery_days'),
    x='avg_delivery_days', y='state',
    orientation='h',
    title='Fastest Delivery States (Avg Days)',
    color='avg_delivery_days',
    color_continuous_scale='RdYlGn_r',
)
fig_delivery.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    coloraxis_showscale=False,
    yaxis_title='',
    xaxis_title='Avg Delivery Days'
)

# 7. Daily Orders Area Chart
fig_daily = px.area(
    df_daily, x='day', y='total_orders',
    title='Daily Orders (Last 6 Months)',
    color_discrete_sequence=[COLORS['blue']]
)
fig_daily.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    xaxis_title='Date',
    yaxis_title='Orders'
)

# 8. New Customers Monthly Bar Chart
fig_new_cust = px.bar(
    df_new_cust, x='month', y='new_customers',
    title='New Customers per Month',
    color_discrete_sequence=[COLORS['purple']]
)
fig_new_cust.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    xaxis_title='Month',
    yaxis_title='New Customers'
)

# 9. Revenue vs Freight Scatter
fig_freight = px.scatter(
    df_freight, x='avg_price', y='avg_freight',
    size='total_items', color='category',
    title='Avg Price vs Avg Freight by Category',
    hover_name='category',
    size_max=40
)
fig_freight.update_layout(
    plot_bgcolor=COLORS['card'],
    paper_bgcolor=COLORS['card'],
    font_color=COLORS['text'],
    title_font_size=16,
    showlegend=False,
    xaxis=dict(type='log', title='Avg Price (R$)'),
    yaxis=dict(type='log', title='Avg Freight (R$)'),
    height=400
)


# ── KPI Card helper ────────────────────────────────────────────────
def kpi_card(title, value, color):
    return dbc.Card([
        dbc.CardBody([
            html.P(title, style={
                'color': COLORS['subtext'],
                'fontSize': '11px',
                'marginBottom': '8px',
                'textTransform': 'uppercase',
                'letterSpacing': '1.5px',
                'fontWeight': '500'
            }),
            html.H2(value, style={
                'color': color,
                'fontWeight': '700',
                'margin': '0',
                'fontSize': '26px'
            })
        ], style={'padding': '20px 24px'})
    ], style={
        'backgroundColor': COLORS['card'],
        'border': f'1px solid {color}33',
        'borderTop': f'3px solid {color}',
        'borderRadius': '12px',
        'height': '100%'
    })


# ── Layout ─────────────────────────────────────────────────────────
app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Olist Sales Dashboard",
                    style={'color': COLORS['green'],
                           'fontWeight': '700',
                           'marginBottom': '4px'}),
            html.P("Brazilian E-Commerce Analytics | 2016–2018",
                   style={'color': COLORS['subtext'], 'fontSize': '14px'})
        ])
    ], style={'padding': '20px 24px'}),

    # KPI Cards
    dbc.Row([
        dbc.Col(kpi_card("Total Orders",
                         f"{int(kpi['total_orders']):,}",
                         COLORS['green']), md=3),
        dbc.Col(kpi_card("Total Revenue",
                         f"R$ {float(kpi['total_revenue']):,.0f}",
                         COLORS['blue']), md=3),
        dbc.Col(kpi_card("Avg Order Value",
                         f"R$ {float(kpi['avg_order_value']):.2f}",
                         COLORS['orange']), md=3),
        dbc.Col(kpi_card("Unique Customers",
                         f"{int(kpi['unique_customers']):,}",
                         COLORS['purple']), md=3),
    ], className='g-3 mb-4'),

    # Row 1 — Revenue trend + Daily orders
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_revenue),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=8),
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_status),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=4),
    ], className='g-3 mb-3'),

    # Row 2 — Top categories + Payment methods
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_cats),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=7),
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_payments),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=5),
    ], className='g-3 mb-3'),

    # Row 3 — States + Delivery
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_states),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=6),
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_delivery),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=6),
    ], className='g-3 mb-3'),

    # Row 4 — Daily orders + New customers
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_daily),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=6),
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_new_cust),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=6),
    ], className='g-3 mb-3'),

    # Row 5 — Scatter full width
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_freight),
                style={'backgroundColor': COLORS['card'],
                       'borderRadius': '12px',
                       'border': 'none'}), md=12),
    ], className='g-3 mb-4'),

], fluid=True, style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh'})


# ── Run ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', 
            port=int(os.environ.get('PORT', 8050)))