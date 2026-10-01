# ABC-15 — Bài giữa kì, số thứ tự 15.
# Chạy tại thư mục bài: python main.py
# Chỉ dùng ba thư viện NumPy, pandas và Matplotlib.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.collections import LineCollection


# 1. Phân tích dữ liệu và trả lời 6 câu hỏi.
def phan_tich(gia, folder="ket_qua"):
    """Tính các câu 1–6; thư mục kết quả cần được tạo trước khi chạy."""
    plt.switch_backend("Agg")
    ngay = pd.date_range("2025-01-01", periods=365)
    tham_chieu = np.r_[10000, gia[:-1, -1]]
    san, tran = tham_chieu * 0.9, tham_chieu * 1.1
    cham_san = np.isclose(gia, san[:, None], atol=1e-5, rtol=0)
    cham_tran = np.isclose(gia, tran[:, None], atol=1e-5, rtol=0)
    bang_gia = np.isclose(gia, tham_chieu[:, None], atol=1e-5, rtol=0)
    vuot_bien = (gia < san[:, None] - 1e-5) | (gia > tran[:, None] + 1e-5)
    bang = pd.DataFrame({"Thang": np.repeat(ngay.month, 7),
                         "Quy": np.repeat(ngay.quarter, 7), "Gia": gia.ravel()})
    # Tất cả 7 giá/ngày đều tham gia thống kê; ddof=0 là độ lệch chuẩn quần thể.
    thang = bang.groupby("Thang")["Gia"].agg(
        Trung_binh="mean", Do_lech_chuan=lambda x: x.std(ddof=0),
        Thap_nhat="min", Cao_nhat="max")
    quy = bang.groupby("Quy")["Gia"].agg(
        Trung_binh="mean", Do_lech_chuan=lambda x: x.std(ddof=0),
        Thap_nhat="min", Cao_nhat="max")
    for thong_ke in [thang, quy]:
        thong_ke["Bien_do"] = thong_ke["Cao_nhat"] - thong_ke["Thap_nhat"]
        thong_ke["CV_phan_tram"] = 100 * thong_ke["Do_lech_chuan"] / thong_ke["Trung_binh"]
    quy["Dau_quy"] = [gia[ngay.quarter == q, 0][0] for q in range(1, 5)]
    quy["Cuoi_quy"] = [gia[ngay.quarter == q, -1][-1] for q in range(1, 5)]
    quy["Thay_doi_phan_tram"] = 100 * (quy["Cuoi_quy"] / quy["Dau_quy"] - 1)
    bat_thuong = pd.DataFrame({"Ngay_so": np.arange(1, 366), "Ngay": ngay.strftime("%d/%m"),
        "Tham_chieu": tham_chieu, "San": san, "Tran": tran,
        "So_lan_cham_san": cham_san.sum(axis=1), "So_lan_cham_tran": cham_tran.sum(axis=1),
        "So_lan_bang_tham_chieu": bang_gia.sum(axis=1), "So_lan_vuot_bien": vuot_bien.sum(axis=1)})
    bat_thuong = bat_thuong[(cham_san | cham_tran | bang_gia | vuot_bien).any(axis=1)]
    for ten, du_lieu in [("thang", thang), ("quy", quy), ("ngay_bat_thuong", bat_thuong)]:
        print("\nBẢNG " + ten.upper())
        print(du_lieu.round(2).to_string(index=ten != "ngay_bat_thuong"))
        du_lieu.to_csv(folder + "/" + ten + ".csv", index=ten != "ngay_bat_thuong", encoding="utf-8-sig")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(10, 4.5), layout="constrained")
    ax.bar(thang.index, thang["Trung_binh"], color="steelblue")
    ax.set(title="Giá trung bình của từng tháng", xlabel="Tháng", ylabel="Giá", xticks=range(1, 13))
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(folder + "/1_trung_binh_thang.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5), layout="constrained")
    ax.boxplot([gia[ngay.month == m].ravel() for m in range(1, 13)])
    ax.set(title="Biểu đồ hộp giá theo tháng", xlabel="Tháng", ylabel="Giá")
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(folder + "/2_boxplot.png", dpi=140)
    plt.close(fig)

    nua_dau, nua_cuoi = gia[ngay.month <= 6].ravel(), gia[ngay.month > 6].ravel()
    khoang = np.linspace(gia.min(), gia.max(), 26)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True, layout="constrained")
    for ax, mau, ten in zip(axes, [nua_dau, nua_cuoi], ["Hai quý đầu năm", "Hai quý cuối năm"]):
        ax.hist(mau, bins=khoang, density=True, color="steelblue", edgecolor="white")
        ax.set(title=ten, xlabel="Giá", ylabel="Mật độ")
        ax.grid(axis="y", alpha=0.2)
    fig.savefig(folder + "/3_histogram.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5), layout="constrained")
    ax.plot(np.arange(1, 366), gia[:, -1], linewidth=1, label="Giá đóng cửa")
    ax.plot(np.arange(1, 366), pd.Series(gia[:, -1]).rolling(30).mean(), label="Trung bình 30 ngày")
    ax.set(title="Xu hướng giá trong năm", xlabel="Ngày thứ", ylabel="Giá")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.savefig(folder + "/4_xu_huong.png", dpi=140)
    plt.close(fig)

    thang_bien_do = thang["Bien_do"].idxmax()
    thang_std = thang["Do_lech_chuan"].idxmax()
    iqr = [np.ptp(np.percentile(gia[ngay.month == m], [25, 75])) for m in range(1, 13)]
    quy_std = quy["Do_lech_chuan"].idxmax()
    quy_cv = quy["CV_phan_tram"].idxmax()
    bien_do_ngay = np.ptp(gia, axis=1)
    ngay_manh = int(bien_do_ngay.argmax())
    thap = np.argwhere(gia == gia.min())
    cao = np.argwhere(gia == gia.max())
    luc_thap = ", ".join(f"ngày {i+1} ({ngay[i]:%d/%m}), phiên {j+1}" for i, j in thap)
    luc_cao = ", ".join(f"ngày {i+1} ({ngay[i]:%d/%m}), phiên {j+1}" for i, j in cao)
    doi_gia = 100 * (gia[-1, -1] / gia[0, 0] - 1)
    tang_giam = "tăng" if doi_gia > 0 else "giảm"
    xanh_giam = np.argwhere((np.diff(gia, axis=1) < -1e-5)
        & (gia[:, 1:] > tham_chieu[:, None] + 1e-5) & ~cham_tran[:, 1:])
    i, j = xanh_giam[0]
    nhan_xet = [
        "ABC-15 — NHẬN XÉT NGẮN CHO 6 CÂU HỎI",
        "Quy ước: dùng 7 giá/ngày; lịch không nhuận 2025 chỉ để gán tháng/quý, không phải năm được cung cấp.",
        "Ngày 1 giả định tham chiếu 10000 (phù hợp sàn 9000, trần 11000). Đơn vị giữ nguyên theo dữ liệu.",
        "Độ lệch chuẩn dùng ddof=0. So sánh giá dùng sai số tuyệt đối 0.00001, rtol=0.",
        "\n1. THÁNG — xem thang.csv và hai hình đầu.",
        f"Giá trung bình cao nhất ở tháng {thang['Trung_binh'].idxmax()}, thấp nhất ở tháng {thang['Trung_binh'].idxmin()}.",
        f"Tháng {thang_bien_do} có biên độ (max−min) lớn nhất: {thang.loc[thang_bien_do, 'Bien_do']:,.2f}.",
        f"Tháng {thang_std} có độ lệch chuẩn lớn nhất: {thang.loc[thang_std, 'Do_lech_chuan']:,.2f}.",
        "Boxplot: hộp từ phân vị 25% đến 75%; đường trong hộp là trung vị. Hộp cao thể hiện 50% giá giữa phân tán hơn.",
        "Râu đến điểm xa nhất còn nằm trong [Q1−1.5×IQR, Q3+1.5×IQR]; các chấm ngoài râu là ngoại lệ theo quy tắc này.",
        f"Tháng {np.argmax(iqr)+1} có hộp cao nhất (IQR = {max(iqr):,.2f}), tức 50% giá giữa phân tán mạnh nhất.",
        f"Mức giá giữa các tháng khác nhau; dùng thêm CV = độ lệch chuẩn / trung bình × 100% để so sánh tương đối.",
        "\n2. QUÝ — xem quy.csv."]
    for q, dong in quy.iterrows():
        nhan_xet.append(f"Quý {q}: trung bình {dong.Trung_binh:,.2f}; độ lệch chuẩn {dong.Do_lech_chuan:,.2f}; "
                        f"biên độ {dong.Bien_do:,.2f}; CV {dong.CV_phan_tram:.2f}%; đầu→cuối quý {dong.Thay_doi_phan_tram:+.2f}%.")
    nhan_xet += [f"Quý {quy_std} phân tán mạnh nhất theo độ lệch chuẩn tuyệt đối; quý {quy_cv} mạnh nhất theo CV.",
        "\n3. NGÀY CÓ YẾU TỐ BẤT THƯỜNG — xem ngay_bat_thuong.csv (một dòng/ngày).",
        f"Có {len(bat_thuong)} ngày được liệt kê: {(cham_san.any(axis=1)).sum()} ngày chạm sàn, "
        f"{(cham_tran.any(axis=1)).sum()} ngày chạm trần, {(bang_gia.any(axis=1)).sum()} ngày bằng tham chiếu; các nhóm có thể trùng nhau.",
        f"Có {vuot_bien.sum()} giá vượt biên. Chạm sàn/trần/tham chiếu là sự kiện cần quan sát, không tự động là lỗi.",
        "\n4. HISTOGRAM — xem hình 3. Hai nửa năm dùng cùng 25 khoảng giá và mật độ, diện tích mỗi histogram bằng 1.",
        f"Hai quý đầu: {nua_dau.size} giá, TB {nua_dau.mean():,.2f}, std {nua_dau.std():,.2f}. "
        f"Hai quý cuối: {nua_cuoi.size} giá, TB {nua_cuoi.mean():,.2f}, std {nua_cuoi.std():,.2f}.",
        "Hai quý cuối có mức giá trung bình cao hơn và phân bố rộng hơn hai quý đầu (độ lệch chuẩn lớn hơn).",
        "So sánh mật độ giúp tránh chênh lệch số quan sát do hai nửa năm có số ngày khác nhau.",
        "\n5. CẢ NĂM — xem hình 4.",
        f"Từ mở cửa đầu năm {gia[0, 0]:,.2f} đến đóng cửa cuối năm {gia[-1, -1]:,.2f}: {tang_giam} {abs(doi_gia):.2f}%.",
        "Giá giảm trong quý 1, phục hồi mạnh quý 2, đạt đỉnh trong quý 3 rồi giảm trong quý 4; không giảm đều cả năm.",
        f"Giá thấp nhất {gia.min():,.2f}: {luc_thap}. Giá cao nhất {gia.max():,.2f}: {luc_cao}.",
        f"Biên độ toàn năm (max−min) là {np.ptp(gia):,.2f}; đây là khoảng giữa hai cực trị, không phải mức thay đổi một ngày.",
        f"Biên độ trong ngày lớn nhất {bien_do_ngay[ngay_manh]:,.2f}, ngày {ngay_manh+1} ({ngay[ngay_manh]:%d/%m}).",
        "\n6. VÌ SAO ĐƯỜNG ĐI XUỐNG VẪN XANH?",
        "Độ dốc so với phiên ngay trước, còn màu so với giá tham chiếu (đóng cửa ngày trước). Giá giảm nhưng vẫn trên tham chiếu thì vẫn xanh lá.",
        f"Ví dụ ngày {i+1} ({ngay[i]:%d/%m}), phiên {j+1}→{j+2}: {gia[i,j]:,.2f}→{gia[i,j+1]:,.2f}; tham chiếu {tham_chieu[i]:,.2f}."]
    with open(folder + "/nhan_xet.txt", "w", encoding="utf-8") as tep:
        tep.write("\n".join(nhan_xet) + "\n")


# 2. Chọn màu và tạo video bằng Matplotlib.
def mau_gia(gia, tham_chieu):
    """Màu được so với giá đóng cửa của ngày trước."""
    if np.isclose(gia, 0.9 * tham_chieu, atol=1e-5, rtol=0):
        return '#38a4ff'  # Sàn: xanh dương.
    if np.isclose(gia, 1.1 * tham_chieu, atol=1e-5, rtol=0):
        return '#cd70ff'  # Trần: tím.
    if np.isclose(gia, tham_chieu, atol=1e-5, rtol=0):
        return '#ffdc4a'  # Tham chiếu: vàng.
    return '#35d273' if gia > tham_chieu else '#ff515b'


def tao_video(gia, thu_muc='static'):
    """Một khung hình ứng với một ngày, có đủ 7 mức giá của ngày đó."""
    plt.switch_backend('Agg')
    plt.rcParams['animation.ffmpeg_path'] = 'tools/ffmpeg.exe'
    if not FFMpegWriter.isAvailable():
        raise RuntimeError('Cần tools/ffmpeg.exe hoặc sửa đường dẫn FFmpeg trong main.py.')

    ngay = np.arange(1, 366)
    lich = pd.date_range('2025-01-01', periods=365)  # Chỉ dùng lịch năm không nhuận.
    tham_chieu = np.r_[10000, gia[:-1, -1]]  # Ngày đầu giả định tham chiếu 10.000.
    mo, dong = gia[:, 0], gia[:, -1]
    thap, cao = gia.min(axis=1), gia.max(axis=1)
    gia_phang = gia.ravel()
    x = np.repeat(ngay, 7) + np.tile(np.linspace(-0.35, 0.35, 7), 365)
    mau_diem = [mau_gia(p, tham_chieu[i // 7]) for i, p in enumerate(gia_phang)]

    # Chia đường tại tham chiếu để phần trên xanh, phần dưới đỏ.
    doan, mau_doan, so_doan = [], [], [0]
    for i in range(1, len(gia_phang)):
        x0, x1, y0, y1 = x[i - 1], x[i], gia_phang[i - 1], gia_phang[i]
        tc = tham_chieu[i // 7]
        if min(y0, y1) < tc < max(y0, y1):
            xc = x0 + (x1 - x0) * (tc - y0) / (y1 - y0)
            doan.extend([[(x0, y0), (xc, tc)], [(xc, tc), (x1, y1)]])
            mau_doan.extend([mau_gia((y0 + tc) / 2, tc), mau_gia((y1 + tc) / 2, tc)])
        else:
            doan.append([(x0, y0), (x1, y1)])
            mau_doan.append(mau_gia((y0 + y1) / 2, tc))
        so_doan.append(len(doan))

    with plt.style.context('dark_background'):
        fig, (tren, duoi) = plt.subplots(2, 1, figsize=(12.8, 7.2), sharex=True)
        fig.subplots_adjust(left=.075, right=.98, bottom=.075, top=.91, hspace=.24)
        for ax in (tren, duoi):
            ax.set_xlim(0, 366)
            ax.set_ylim(0, cao.max() * 1.12)
            ax.set_ylabel('Giá')
            ax.grid(alpha=.15)
            ax.tick_params(labelsize=10)
        tren.set_title('Biểu đồ nến', loc='left', fontsize=12)
        duoi.set_title('Đường giá', loc='left', fontsize=12)
        duoi.set_xlabel('Ngày')
        duoi.set_xticks(np.arange(0, 361, 30))
        tieu_de = fig.suptitle('ABC-15', fontsize=16)

        # Thân nến: khoảng mở–đóng. Râu nến: khoảng thấp nhất–cao nhất.
        mau_nen = [mau_gia(dong[i], tham_chieu[i]) for i in range(365)]
        nen = tren.bar(ngay, abs(dong - mo), bottom=np.minimum(mo, dong),
                       width=.65, color=mau_nen, linewidth=0)
        rau = LineCollection([], linewidths=.8)
        than_ngang = LineCollection([], linewidths=2)
        tren.add_collection(rau)
        tren.add_collection(than_ngang)
        duong = LineCollection([], linewidths=1.2)
        duoi.add_collection(duong)
        diem = duoi.scatter([], [], s=5, zorder=3)
        hien_tai, = duoi.plot([], [], 'o', markersize=5, zorder=4)

        def cap_nhat(i):
            n = (i + 1) * 7
            for j, cot in enumerate(nen):
                cot.set_visible(j <= i)
            rau.set_segments([[(j + 1, thap[j]), (j + 1, cao[j])] for j in range(i + 1)])
            rau.set_color(mau_nen[:i + 1])
            # Khi mở cửa bằng đóng cửa, thân nến là một gạch ngang.
            bang_nhau = [j for j in range(i + 1) if np.isclose(mo[j], dong[j], atol=1e-5, rtol=0)]
            than_ngang.set_segments([[(j + .7, mo[j]), (j + 1.3, mo[j])] for j in bang_nhau])
            than_ngang.set_color([mau_nen[j] for j in bang_nhau])
            duong.set_segments(doan[:so_doan[n - 1]])
            duong.set_color(mau_doan[:so_doan[n - 1]])
            diem.set_offsets(np.column_stack((x[:n], gia_phang[:n])))
            diem.set_facecolor(mau_diem[:n])
            hien_tai.set_data([x[n - 1]], [dong[i]])
            hien_tai.set_color(mau_nen[i])
            tieu_de.set_text(f'ABC-15  |  Ngày {i + 1} ({lich[i]:%d/%m})  |  Giá: {dong[i]:,.2f}')

        writer = FFMpegWriter(fps=6, codec='libx264',
                             extra_args=['-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'])
        with writer.saving(fig, thu_muc + '/video/abc15.mp4', dpi=100):
            for i in range(365):
                cap_nhat(i)
                writer.grab_frame()
                if (i + 1) % 60 == 0:
                    print(f'Đã xuất {i + 1}/365 ngày', flush=True)
        fig.savefig(thu_muc + '/img/xem_truoc.png', dpi=100)
        plt.close(fig)
    print('Đã xuất video abc15.mp4 (365 ngày, khoảng 61 giây).')

# 3. Đọc dữ liệu, tạo kết quả và xuất video.
if __name__ == '__main__':
    gia = pd.read_csv('data/abc-15.csv', header=None).to_numpy(dtype=float)
    if gia.shape != (365, 7) or not np.isfinite(gia).all() or (gia <= 0).any():
        raise ValueError('Dữ liệu phải gồm 365 ngày × 7 giá hợp lệ, đều lớn hơn 0.')
    phan_tich(gia)
    tao_video(gia)
    print('Hoàn thành! Mở mo_web.bat để xem bài.')
