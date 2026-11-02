from pathlib import Path  # Có sẵn trong Python, dùng để tạo thư mục.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Chạy: python xuat_ket_qua.py
# Kết quả lưu ở thư mục ket_qua_6_cau cạnh file này.
thu_muc = Path(__file__).resolve().parent
ket_qua = thu_muc / 'ket_qua_6_cau'
ket_qua.mkdir(exist_ok=True)
plt.switch_backend('Agg')  # Lưu ảnh, không mở cửa sổ biểu đồ.
noi_dung = []
quy_uoc = (
    'Nguồn: data/abc-15.csv, dùng đủ 7 giá mỗi ngày.\n'
    'Đề không ghi năm: dùng lịch 2025 (không nhuận) để chia tháng/quý.\n'
    'Độ lệch chuẩn quần thể: ddof=0. Đơn vị giá theo dữ liệu gốc.\n'
    'Tham chiếu ngày đầu giả định 10.000; các ngày sau là đóng cửa hôm trước.\n'
)


def ghi(*cac_phan):
    """Vừa in kết quả, vừa giữ lại để lưu vào tệp TXT."""
    dong = ' '.join(str(x) for x in cac_phan)
    print(dong)
    noi_dung.append(dong)


def luu_cau(so_cau):
    (ket_qua / f'cau_{so_cau}.txt').write_text(
        quy_uoc + '\n' + '\n'.join(noi_dung), encoding='utf-8-sig')
    noi_dung.clear()


def luu_anh(fig, ten):
    fig.savefig(ket_qua / ten, dpi=160, bbox_inches='tight')
    plt.close(fig)


# CHUẨN BỊ DỮ LIỆU
gia = pd.read_csv(thu_muc / 'data/abc-15.csv', header=None).to_numpy(dtype=float)
if gia.shape != (365, 7) or not np.isfinite(gia).all() or (gia <= 0).any():
    raise ValueError('Dữ liệu cần có 365 ngày × 7 giá hợp lệ, đều lớn hơn 0.')

# Đề không ghi năm: dùng lịch không nhuận 2025 để chia tháng/quý.
ngay = pd.date_range('2025-01-01', periods=365)
bang = pd.DataFrame({
    'Thang': np.repeat(ngay.month, 7),
    'Quy': np.repeat(ngay.quarter, 7),
    'Gia': gia.ravel()
})
# Ngày đầu chưa có đóng cửa hôm trước nên giả định tham chiếu 10.000.
tham_chieu = np.r_[10000, gia[:-1, -1]]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11})
ghi('Dùng cả 7 giá/ngày. Độ lệch chuẩn quần thể: ddof=0.')


# CÂU 1: THỐNG KÊ THEO THÁNG, BIỂU ĐỒ CỘT VÀ BOXPLOT
ghi('\nCÂU 1 — THEO THÁNG')
thang = bang.groupby('Thang')['Gia'].agg(
    Trung_binh='mean', Do_lech_chuan=lambda x: x.std(ddof=0),
    Thap_nhat='min', Cao_nhat='max'
)
thang['Bien_do'] = thang['Cao_nhat'] - thang['Thap_nhat']
ghi(thang.round(2).to_string())
ghi('Tháng có giá trung bình cao nhất:', thang['Trung_binh'].idxmax())
ghi('Tháng có giá trung bình thấp nhất:', thang['Trung_binh'].idxmin())
ghi('Tháng có biên độ lớn nhất:', thang['Bien_do'].idxmax())
ghi('Tháng có độ lệch chuẩn lớn nhất:', thang['Do_lech_chuan'].idxmax())

fig, ax = plt.subplots(figsize=(10, 4.5), layout='constrained')
ax.bar(thang.index, thang['Trung_binh'], color='steelblue')
ax.set(title='Giá trung bình từng tháng', xlabel='Tháng', ylabel='Giá', xticks=range(1, 13))
ax.grid(axis='y', alpha=.2)

luu_anh(fig, 'cau_1_gia_trung_binh.png')

gia_thang = [gia[ngay.month == m].ravel() for m in range(1, 13)]
fig, ax = plt.subplots(figsize=(10, 4.5), layout='constrained')
ax.boxplot(gia_thang)
ax.set(title='Boxplot giá theo tháng', xlabel='Tháng', ylabel='Giá')
ax.grid(axis='y', alpha=.2)
luu_anh(fig, 'cau_1_boxplot.png')
iqr = [np.percentile(x, 75) - np.percentile(x, 25) for x in gia_thang]
ghi('Hộp chứa 50% giá ở giữa; đường trong hộp là trung vị.')
ghi('Râu đến điểm xa nhất trong [Q25 - 1.5*IQR, Q75 + 1.5*IQR]; chấm ngoài râu là ngoại lệ.')
ghi(f'Tháng {np.argmax(iqr) + 1} có hộp cao nhất, IQR = {max(iqr):,.2f}.')


thang.to_csv(ket_qua / 'cau_1_theo_thang.csv', encoding='utf-8-sig')
luu_cau(1)


# CÂU 2: ĐÁNH GIÁ TỪNG QUÝ
ghi('\nCÂU 2 — THEO QUÝ')
quy = bang.groupby('Quy')['Gia'].agg(
    Trung_binh='mean', Do_lech_chuan=lambda x: x.std(ddof=0),
    Thap_nhat='min', Cao_nhat='max'
)
quy['Bien_do'] = quy['Cao_nhat'] - quy['Thap_nhat']
quy['CV_phan_tram'] = quy['Do_lech_chuan'] / quy['Trung_binh'] * 100
quy['Dau_quy'] = [gia[ngay.quarter == q, 0][0] for q in range(1, 5)]
quy['Cuoi_quy'] = [gia[ngay.quarter == q, -1][-1] for q in range(1, 5)]
quy['Thay_doi_phan_tram'] = (quy['Cuoi_quy'] / quy['Dau_quy'] - 1) * 100
ghi(quy.round(2).to_string())
ghi('Quý có độ lệch chuẩn lớn nhất:', quy['Do_lech_chuan'].idxmax())
ghi('Quý có CV lớn nhất:', quy['CV_phan_tram'].idxmax())
ghi('Đầu→cuối quý: giá mở cửa ngày đầu so với đóng cửa ngày cuối quý.')


for q, dong_quy in quy.iterrows():
    huong = 'tăng' if dong_quy['Thay_doi_phan_tram'] >= 0 else 'giảm'
    ghi(f"Quý {q}: giá đầu–cuối quý {huong} {abs(dong_quy['Thay_doi_phan_tram']):.2f}%, "
        f"độ lệch chuẩn {dong_quy['Do_lech_chuan']:,.2f}, CV {dong_quy['CV_phan_tram']:.2f}%.")
ghi('Độ lệch chuẩn đo mức phân tán giá; CV = độ lệch chuẩn / trung bình × 100%.')
quy.to_csv(ket_qua / 'cau_2_theo_quy.csv', encoding='utf-8-sig')
luu_cau(2)


# CÂU 3: LIỆT KÊ CÁC NGÀY CÓ SỰ KIỆN BẤT THƯỜNG
ghi('\nCÂU 3 — NGÀY CÓ SỰ KIỆN BẤT THƯỜNG')
san, tran = .9 * tham_chieu, 1.1 * tham_chieu
# Dùng sai số 0.00001 để tránh lỗi so sánh số thực.
cham_san = np.isclose(gia, san[:, None], atol=1e-5, rtol=0)
cham_tran = np.isclose(gia, tran[:, None], atol=1e-5, rtol=0)
bang_tc = np.isclose(gia, tham_chieu[:, None], atol=1e-5, rtol=0)
vuot_bien = (gia < san[:, None] - 1e-5) | (gia > tran[:, None] + 1e-5)

bat_thuong = pd.DataFrame({
    'Ngay_so': np.arange(1, 366), 'Ngay': ngay.strftime('%d/%m'),
    'Tham_chieu': tham_chieu, 'San': san, 'Tran': tran,
    'So_lan_cham_san': cham_san.sum(axis=1),
    'So_lan_cham_tran': cham_tran.sum(axis=1),
    'So_lan_bang_tham_chieu': bang_tc.sum(axis=1),
    'So_lan_vuot_bien': vuot_bien.sum(axis=1)
})
co_su_kien = (cham_san | cham_tran | bang_tc | vuot_bien).any(axis=1)
bat_thuong = bat_thuong[co_su_kien]
ghi(bat_thuong.round(2).to_string(index=False))
ghi('Tổng số ngày có sự kiện:', len(bat_thuong))
ghi('Số ngày chạm sàn:', cham_san.any(axis=1).sum())
ghi('Số ngày chạm trần:', cham_tran.any(axis=1).sum())
ghi('Số ngày bằng tham chiếu:', bang_tc.any(axis=1).sum())
ghi('Số ngày vượt biên:', vuot_bien.any(axis=1).sum())
ghi('Một ngày có thể vừa chạm sàn vừa chạm trần; chạm biên không tự động là lỗi dữ liệu.')


bat_thuong.to_csv(ket_qua / 'cau_3_ngay_bat_thuong.csv', index=False, encoding='utf-8-sig')
luu_cau(3)


# CÂU 4: HISTOGRAM HAI NỬA NĂM
ghi('\nCÂU 4 — HAI NỬA NĂM')
nua_dau = gia[ngay.month <= 6].ravel()
nua_cuoi = gia[ngay.month > 6].ravel()
hai_nua = pd.DataFrame({
    'Giai_doan': ['Hai quý đầu', 'Hai quý cuối'],
    'So_gia': [nua_dau.size, nua_cuoi.size],
    'Trung_binh': [nua_dau.mean(), nua_cuoi.mean()],
    'Do_lech_chuan': [nua_dau.std(ddof=0), nua_cuoi.std(ddof=0)]
})
ghi(hai_nua.round(2).to_string(index=False))
khoang = np.linspace(gia.min(), gia.max(), 26)  # 26 mép tạo 25 khoảng giá.
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True, layout='constrained')
for ax, du_lieu, ten in zip(axes, [nua_dau, nua_cuoi], ['Hai quý đầu', 'Hai quý cuối']):
    ax.hist(du_lieu, bins=khoang, density=True, color='steelblue', edgecolor='white')
    ax.set(title=ten, xlabel='Giá', ylabel='Mật độ')
ghi('Dùng cùng các khoảng giá và mật độ để so sánh hai nhóm có số quan sát khác nhau.')


luu_anh(fig, 'cau_4_phan_bo_gia.png')
hai_nua.to_csv(ket_qua / 'cau_4_hai_nua_nam.csv', index=False, encoding='utf-8-sig')
ghi('Hai quý cuối có giá trung bình', 'cao hơn' if nua_cuoi.mean() > nua_dau.mean() else 'thấp hơn',
    'hai quý đầu; độ lệch chuẩn', 'lớn hơn.' if nua_cuoi.std() > nua_dau.std() else 'nhỏ hơn.')
luu_cau(4)


# CÂU 5: XU HƯỚNG NĂM, CỰC TRỊ VÀ BIÊN ĐỘ
ghi('\nCÂU 5 — CẢ NĂM')
thay_doi = (gia[-1, -1] / gia[0, 0] - 1) * 100
ghi(f'Mở cửa đầu năm: {gia[0, 0]:,.2f}; đóng cửa cuối năm: {gia[-1, -1]:,.2f}.')
ghi(f'Thay đổi đầu→cuối năm: {thay_doi:.2f}%.')
for ten, muc_gia in [('Thấp nhất', gia.min()), ('Cao nhất', gia.max())]:
    for i, j in np.argwhere(gia == muc_gia):
        ghi(f'{ten}: {muc_gia:,.2f}, ngày {i + 1} ({ngay[i]:%d/%m}), phiên {j + 1}.')
ghi(f'Biên độ toàn năm: {np.ptp(gia):,.2f}.')
bien_do_ngay = np.ptp(gia, axis=1)
i = int(bien_do_ngay.argmax())
ghi(f'Biên độ trong ngày lớn nhất: {bien_do_ngay[i]:,.2f}, ngày {i + 1} ({ngay[i]:%d/%m}).')

fig, ax = plt.subplots(figsize=(10, 4.5), layout='constrained')
ax.plot(np.arange(1, 366), gia[:, -1], linewidth=1, label='Giá đóng cửa')
ax.plot(np.arange(1, 366), pd.Series(gia[:, -1]).rolling(30).mean(), label='Trung bình 30 ngày')
ax.set(title='Xu hướng giá cả năm', xlabel='Ngày thứ', ylabel='Giá')
ax.legend()
ax.grid(alpha=.2)


luu_anh(fig, 'cau_5_xu_huong_nam.png')
ghi('Xét đầu–cuối năm, giá', 'tăng.' if thay_doi >= 0 else 'giảm.')
ghi('Giá không biến động một chiều; xem đường đóng cửa và trung bình 30 ngày để nhận ra các đợt tăng giảm.')
ghi('Biên độ cả năm là giá cao nhất trừ thấp nhất ở hai thời điểm; biên độ trong ngày chỉ dùng giá của một ngày.')
luu_cau(5)


# CÂU 6: TÌM VÍ DỤ ĐƯỜNG ĐI XUỐNG NHƯNG VẪN XANH
ghi('\nCÂU 6 — ĐƯỜNG ĐI XUỐNG NHƯNG VẪN XANH')
giam_nhung_xanh = (
    (np.diff(gia, axis=1) < -1e-5)
    & (gia[:, 1:] > tham_chieu[:, None] + 1e-5)
    & ~np.isclose(gia[:, 1:], 1.1 * tham_chieu[:, None], atol=1e-5, rtol=0)
)
vi_du = np.argwhere(giam_nhung_xanh)
if len(vi_du):
    i, j = vi_du[0]
    ghi(f'Ngày {i + 1} ({ngay[i]:%d/%m}), phiên {j + 1}→{j + 2}:')
    ghi(f'Giá: {gia[i, j]:,.2f}→{gia[i, j + 1]:,.2f}; tham chiếu: {tham_chieu[i]:,.2f}.')
else:
    ghi('Dữ liệu không có ví dụ giá giảm nhưng vẫn xanh lá.')
ghi('Độ dốc so với phiên liền trước; màu so với đóng cửa ngày trước.')
ghi('Giá giảm nhưng vẫn trên tham chiếu và khác trần thì vẫn xanh lá.')

luu_cau(6)
print(f'\nĐã xuất tất cả kết quả tại: {ket_qua}')
