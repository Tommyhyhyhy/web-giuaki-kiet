
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.collections import LineCollection


THU_MUC = Path(__file__).resolve().parent
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount('/static', StaticFiles(directory=THU_MUC / 'static'), name='static')


@app.get('/')
def trang_chu():
    return FileResponse(THU_MUC / 'templates' / 'index.html')


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
