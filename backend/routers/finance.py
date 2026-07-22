"""Finance & Statistics endpoints — stats, types, summary, trend, top-customers."""

from fastapi import APIRouter

from backend.database import get_db
from backend.models import vben_response
from backend.utils.amount_converter import convert_fields, convert_list_fields

router = APIRouter(tags=["finance"])


@router.get('/api/stats')
def get_stats():
    db = get_db()
    c = db.execute('SELECT COUNT(*) FROM contracts').fetchone()[0]
    total_amt = db.execute('SELECT COALESCE(SUM(contract_amount),0) FROM contracts').fetchone()[0]
    fin = db.execute('''
        SELECT COALESCE(SUM(invoice_total),0) as inv,
               COALESCE(SUM(payment_total),0) as pay
        FROM current_finance_view
    ''').fetchone()
    fin2 = db.execute('''
        SELECT COALESCE(SUM(sub_invoice_total),0) as sub_inv,
               COALESCE(SUM(sub_payment_total),0) as sub_pay
        FROM finance_records
        WHERE record_id IN (SELECT MAX(record_id) FROM finance_records GROUP BY project_id)
    ''').fetchone()
    stages = db.execute('SELECT COUNT(*) FROM stages').fetchone()[0]
    payments = db.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
    deliverables = db.execute('SELECT COUNT(*) FROM deliverables').fetchone()[0]
    db.close()
    rate = round(fin['pay'] / fin['inv'] * 100, 1) if fin['inv'] else 0
    stats = {
        'contract_count': c,
        'total_amount': round(total_amt, 2),
        'invoiced': round(fin['inv'], 2),
        'received': round(fin['pay'], 2),
        'receipt_rate': rate,
        'sub_invoiced': round(fin2['sub_inv'], 2),
        'sub_paid': round(fin2['sub_pay'], 2),
        'stages': stages,
        'payments': payments,
        'deliverables': deliverables,
    }
    convert_fields(stats, ['total_amount', 'invoiced', 'received', 'sub_invoiced', 'sub_paid'])
    return vben_response(stats)


@router.get('/api/stats/types')
def get_type_distribution():
    db = get_db()
    rows = db.execute('''
        SELECT COALESCE(cta.contract_category, c.project_type) as type,
               COUNT(*) as cnt, COALESCE(SUM(c.contract_amount),0) as total
        FROM contracts c
        LEFT JOIN contract_type_attributes cta ON c.contract_id = cta.contract_id
        WHERE c.contract_amount > 0
        GROUP BY type
        ORDER BY total DESC
    ''').fetchall()
    db.close()
    return vben_response({'types': [dict(r) for r in rows]})


@router.get('/api/finance/summary')
def get_finance_summary():
    db = get_db()
    rows = db.execute('''
        SELECT cv.project_id, cv.project_name, cv.invoice_total, cv.payment_total,
               cv.payment_unreceived, fr.sub_invoice_total, fr.sub_payment_total, cv.subcontractor
        FROM current_finance_view cv
        LEFT JOIN finance_records fr ON cv.project_id = fr.project_id
            AND fr.record_id IN (SELECT MAX(record_id) FROM finance_records GROUP BY project_id)
        ORDER BY cv.invoice_total DESC
    ''').fetchall()
    items = [dict(r) for r in rows]
    for item in items:
        convert_fields(item, ['contract_amount', 'invoice_total', 'payment_total', 'sub_invoice_total', 'sub_payment_total', 'subcontract_amount'])
    db.close()
    return vben_response({'items': items})


@router.get('/api/finance/trend')
def get_finance_trend():
    db = get_db()
    rows = db.execute('''
        SELECT batch_id,
               COALESCE(SUM(invoice_total),0) as inv,
               COALESCE(SUM(payment_total),0) as pay,
               import_time
        FROM finance_records
        WHERE batch_id IS NOT NULL
        GROUP BY batch_id
        ORDER BY import_time
    ''').fetchall()
    db.close()
    return vben_response({'trends': [dict(r) for r in rows]})


@router.get('/api/finance/top-customers')
def get_top_customers(limit: int = 10):
    db = get_db()
    rows = db.execute('''
        SELECT party_a as customer, COUNT(*) as cnt, COALESCE(SUM(contract_amount),0) as total
        FROM contracts
        WHERE party_a IS NOT NULL AND party_a != ''
        GROUP BY party_a
        ORDER BY total DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    db.close()
    return vben_response({'customers': [dict(r) for r in rows]})
