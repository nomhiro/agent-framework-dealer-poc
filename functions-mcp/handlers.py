import logging
import json
from sample_data import SAMPLE_INVENTORY


def handle_vehicle_models_get(body: dict) -> dict:
    """購入可能な車種一覧取得処理"""
    vehicle_models = []
    total_grades = 0
    total_engine_options = 0

    for model in SAMPLE_INVENTORY:
        model_info = {
            "model_id": model["model_id"],
            "model_name": model["model_name"],
            "vehicle_type": model.get("vehicle_type"),
            "grades": []
        }

        for grade in model.get("grades", []) :
            grade_info = {
                "grade_id": grade["grade_id"],
                "grade_name": grade["grade_name"],
                "engine_options": []
            }

            for engine in grade.get("engine_options", []) :
                grade_info["engine_options"].append({
                    "engine_id": engine["engine_id"],
                    "engine_type": engine.get("engine_type"),
                    "orderable": engine.get("orderable", True),
                    "est_lead_weeks": engine.get("lead_time_weeks", 12),
                    "price_estimate": engine.get("price", 0)
                })
                total_engine_options += 1

            model_info["grades"].append(grade_info)
            total_grades += 1

        vehicle_models.append(model_info)

    return {
        "vehicle_models": vehicle_models,
        "total_models": len(vehicle_models),
        "total_grades": total_grades,
        "total_engine_options": total_engine_options,
        "basis": "sample_inventory"
    }


def handle_leadtime_get(body: dict) -> dict:
    """納期情報取得処理（入力: model_ids のみ）
    指定された model_id ごとに、そのモデルの全グレードと各エンジンオプションの納期情報を返す
    """
    model_ids = body.get("model_ids") or []
    # Normalize input: model_ids may be passed as a JSON string or a simple comma-separated string
    if isinstance(model_ids, str):
        # try parse JSON string first
        try:
            parsed = json.loads(model_ids)
            if isinstance(parsed, list):
                model_ids = parsed
            elif isinstance(parsed, str):
                model_ids = [parsed]
            else:
                # fallback to string splitting
                model_ids = [str(parsed)]
        except Exception:
            # not a JSON string, try comma separated list like 'CROWN,AQUA'
            s = model_ids.strip()
            if s.startswith('[') and s.endswith(']'):
                s = s[1:-1]
            parts = [p.strip().strip('"').strip("'") for p in s.split(',') if p.strip()]
            model_ids = parts
    # If single id provided (not list), wrap into list
    if not isinstance(model_ids, list):
        model_ids = [model_ids]
    items = []

    for mid in model_ids:
        found_model = next((m for m in SAMPLE_INVENTORY if m.get("model_id") == mid), None)
        if not found_model:
            # 見つからないモデルはデフォルト納期を返す
            items.append({
                "model_id": mid,
                "est_lead_weeks": 12,
                "grades": []
            })
            continue

        model_entry = {
            "model_id": found_model.get("model_id"),
            "model_name": found_model.get("model_name"),
            "grades": []
        }

        for grade in found_model.get("grades", []):
            grade_entry = {
                "grade_id": grade.get("grade_id"),
                "grade_name": grade.get("grade_name"),
                "engine_options": []
            }
            for engine in grade.get("engine_options", []):
                grade_entry["engine_options"].append({
                    "engine_id": engine.get("engine_id"),
                    "engine_type": engine.get("engine_type"),
                    "orderable": engine.get("orderable", True),
                    "est_lead_weeks": engine.get("lead_time_weeks", 12),
                    "price": engine.get("price", 0),
                    "build_slot": "A1",
                    "plant_id": "plant-01"
                })
            model_entry["grades"].append(grade_entry)

        items.append(model_entry)

    return {"items": items}


def handle_quotation_calc(body: dict) -> dict:
    """サブスクリプション月額料金計算（PoC）
    入力例（body）:
      - vehicle_price (number) または engine_id
      - subscription_term_months (int, default 36)
      - included_mileage_per_month (number, optional)
      - maintenance_included (bool, optional)
      - discount_percent (number, optional)
    出力:
      - monthly_fee, breakdown, total_cost, term_months
    """
    engine_id = body.get("engine_id")
    vehicle_price = int(body.get("vehicle_price", 0) or 0)

    # エンジンIDから価格を取得（必要なら）
    if engine_id and vehicle_price == 0:
        for model in SAMPLE_INVENTORY:
            for grade in model.get("grades", []):
                for engine in grade.get("engine_options", []):
                    if engine.get("engine_id") == engine_id:
                        vehicle_price = int(engine.get("price", 0) or 0)
                        break
                if vehicle_price > 0:
                    break
            if vehicle_price > 0:
                break

    months = int(body.get("subscription_term_months", 36) or 36)
    maintenance_included = bool(body.get("maintenance_included", False))
    included_mileage = body.get("included_mileage_per_month")
    discount_percent = float(body.get("discount_percent", 0) or 0)

    # PoC 用の簡易計算ロジック:
    # - base: 車両価格に対する月額の係数（例: 1.7% / month を使用）
    # - maintenance: 固定の月額追加（簡易値）
    # - tax: base に対する軽微な料率
    # - discount: 割引率を base に対して適用
    if vehicle_price <= 0:
        base_month = 0
    else:
        base_month = round(vehicle_price * 0.017)  # PoC の係数

    maintenance_fee = 3000 if maintenance_included else 0
    tax = round(base_month * 0.015)
    discount_amount = round(base_month * (discount_percent / 100.0))

    monthly_fee = max(0, base_month + maintenance_fee + tax - discount_amount)
    total_cost = monthly_fee * months

    breakdown = {
        "base": base_month,
        "maintenance": maintenance_fee,
        "tax": tax,
        "discount": -discount_amount
    }

    return {
        "monthly_fee": int(monthly_fee),
        "breakdown": breakdown,
        "total_cost": int(total_cost),
        "term_months": months,
        "vehicle_price_used": int(vehicle_price)
    }


def handle_finance_precheck(body: dict) -> dict:
    """
    融資事前審査処理
    顧客の年収と希望借入額から簡易的な信用スコアリングを行う
    """
    # Backward compatibility: accept either top-level fields or a customer_profile object
    profile = body.get("customer_profile") or {}
    # prefer top-level if present
    income = body.get("income") if body.get("income") is not None else profile.get("income", 0)
    requested = body.get("requested_amount") if body.get("requested_amount") is not None else profile.get("requested_amount", 0)
    age = body.get("age") if body.get("age") is not None else profile.get("age")
    employment_status = body.get("employment_status") if body.get("employment_status") is not None else profile.get("employment_status")
    existing_debt = body.get("existing_debt") if body.get("existing_debt") is not None else profile.get("existing_debt", 0)
    dependents = body.get("dependents") if body.get("dependents") is not None else profile.get("dependents", 0)

    try:
        requested = int(requested or 0)
    except Exception:
        requested = 0
    try:
        income = int(income or 0)
    except Exception:
        income = 0

    # バリデーション: 年収は必須（0は無効とみなす）、希望借入額も必須
    if not income or income <= 0:
        return {
            "error": "missing_required_parameter",
            "message": "年収情報が必要です。customer_profile.income または top-level の income を指定してください。"
        }
    if not requested or requested <= 0:
        return {
            "error": "missing_required_parameter",
            "message": "希望借入額（requested_amount）が必要です。正の数を指定してください。"
        }

    # 年収と借入額の比率に基づいてスコアを計算（簡易）
    score = 0
    if income <= 0:
        score = 10  # 年収情報がない場合は最低スコア
    else:
        # 借入希望額がゼロの場合は高評価
        if requested <= 0:
            score = 100
        else:
            ratio = income / max(requested, 1)  # 年収対借入額比率
            score = int(min(100, ratio * 10))   # 10倍して100点満点にスケール

    # 簡易的なマイナス要素の反映（既存借入や扶養人数で減点）
    if existing_debt:
        try:
            ed = int(existing_debt)
            # 既存借入が年収の一定割合を超える場合減点
            if income > 0 and ed > income * 0.5:
                score = max(0, score - 20)
        except Exception:
            pass
    if dependents:
        try:
            d = int(dependents)
            # 扶養が多いと減点（簡易）
            score = max(0, score - min(10, d * 2))
        except Exception:
            pass

    # スコアに基づいて格付けと承認判定を決定
    if score >= 80:
        rating = "AAA"
        approved = True
    elif score >= 60:
        rating = "AA"
        approved = True
    elif score >= 40:
        rating = "A"
        approved = True
    else:
        rating = "B"
        approved = False

    return {
        "score": score,             # 信用スコア（100点満点）
        "rating": rating,           # 格付け（AAA, AA, A, B）
        "approved": approved,       # 承認判定
        "annual_income": income,    # 年収
        "requested_amount": requested  # 希望借入額
    }


def handle_reservations_create(body: dict) -> dict:
    """
    予約作成処理
    試乗予約やサービス予約を作成し、時間の競合をチェックする
    engine_idが指定されている場合は、そのエンジンオプションでの予約として処理する
    """
    customer_id = body.get("customer_id")        # 顧客ID
    vehicle_id = body.get("vehicle_id")          # 車両ID（後方互換性のため保持）
    grade_id = body.get("grade_id")              # グレードID（後方互換性）
    engine_id = body.get("engine_id")            # エンジンID（新しい構造に対応）
    preferred_times = body.get("preferred_times")  # 希望時間のリスト（必須）

    # バリデーション: 予約に必要な項目をチェック
    missing = []
    if not customer_id:
        missing.append("customer_id")
    if not vehicle_id:
        missing.append("vehicle_id")
    if not grade_id:
        missing.append("grade_id")
    if not engine_id:
        missing.append("engine_id")
    if not preferred_times:
        missing.append("preferred_times")

    if missing:
        return {
            "error": "missing_required_parameters",
            "message": "予約に必要なパラメータが不足しています: {}".format(", ".join(missing))
        }

    # エンジンIDから車種・グレード・エンジン情報を取得
    vehicle_info = None
    if engine_id:
        for model in SAMPLE_INVENTORY:
            for grade in model.get("grades", []):
                for engine in grade.get("engine_options", []):
                    if engine.get("engine_id") == engine_id:
                        vehicle_info = {
                            "model_id": model["model_id"],
                            "model_name": model.get("model_name"),
                            "grade_id": grade["grade_id"],
                            "grade_name": grade.get("grade_name"),
                            "engine_id": engine["engine_id"],
                            "engine_type": engine.get("engine_type")
                        }
                        break
                if vehicle_info:
                    break
            if vehicle_info:
                break

    # グレードIDから情報を取得（後方互換性）
    elif grade_id:
        for model in SAMPLE_INVENTORY:
            for grade in model.get("grades", []):
                if grade.get("grade_id") == grade_id:
                    vehicle_info = {
                        "model_id": model["model_id"],
                        "model_name": model.get("model_name"),
                        "grade_id": grade["grade_id"],
                        "grade_name": grade.get("grade_name")
                    }
                    break
            if vehicle_info:
                break

    confirmed = True  # 予約確定フラグ
    scheduled_time = preferred_times[0] if preferred_times else None  # 予約確定時間
    conflicts = []    # 競合情報

    # 簡易的な競合チェック（実際の実装では予約データベースをチェック）
    # preferred_times は配列を想定
    if isinstance(preferred_times, str):
        # 文字列で渡されていたら配列にする
        preferred_times = [preferred_times]
    if "2025-10-10T09:00" in (preferred_times or []):
        confirmed = False  # 競合があるため確定できない
        conflicts.append({
            "time": "2025-10-10T09:00",
            "reason": "slot_taken"
        })

    result = {
        "reservation_id": "resv-" + (customer_id or "anon"),
        "confirmed": confirmed,
        "scheduled_time": scheduled_time,
        "conflicts": conflicts
    }

    if vehicle_info:
        result["vehicle_info"] = vehicle_info
    elif vehicle_id:
        result["vehicle_id"] = vehicle_id

    return result


def health_status() -> dict:
    """ヘルスチェック用のステータス情報を返す"""
    return {"status": "healthy"}
