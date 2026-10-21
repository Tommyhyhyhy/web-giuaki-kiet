from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter

THU_MUC = Path(__file__).resolve().parent


def mau_gia(gia, tham_chieu):
    if np.isclose(gia, 0.9 * tham_chieu, rtol=0, atol=1e-5):
        return 'deepskyblue'
    if np.isclose(gia, 1.1 * tham_chieu, rtol=0, atol=1e-5):
        return 'magenta'
    if np.isclose(gia, tham_chieu, rtol=0, atol=1e-5):
        return 'yellow'
    return 'green' if gia > tham_chieu else 'red'


def tao_video(gia, tep_video=THU_MUC / 'output/abc15_code_gon.mp4'):
    plt.switch_backend('Agg')
    plt.style.use('dark_background')
    ffmpeg = THU_MUC / 'tools/ffmpeg.exe'
    plt.rcParams['animation.ffmpeg_path'] = str(
        ffmpeg if ffmpeg.exists() else Path('D:/gki/tools/ffmpeg.exe'))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 16,
                         'axes.linewidth': 0.9, 'path.simplify': False})
    Path(tep_video).parent.mkdir(parents=True, exist_ok=True)
    so_ngay = len(gia)
    ngay = np.arange(so_ngay)
    thap, cao, dong = gia.min(axis=1), gia.max(axis=1), gia[:, -1]
    tham_chieu = np.r_[10000, dong[:-1]]
    min_da_co = max_da_co = dong[0]

    fig, (tren, duoi) = plt.subplots(2, 1, figsize=(16.6, 9.86), sharex=True)
    fig.subplots_adjust(left=0.0927, right=0.9885, bottom=0.0862, top=0.9787, hspace=0.08)
    gioi_han = np.ceil(cao.max() / 5000) * 5000
    for ax in (tren, duoi):
        ax.set(xlim=(-5, so_ngay + 30), ylim=(-0.05 * gioi_han, 1.05 * gioi_han))
        ax.set_xticks(np.arange(0, so_ngay, 30))
        ax.set_yticks(np.arange(0, gioi_han + 1, 5000))
        ax.yaxis.set_major_formatter('{x:,.0f}')
        ax.set_ylabel('VND', labelpad=9)
        ax.tick_params(length=6, width=0.9, pad=6)
    duoi.set_xlabel('Date', labelpad=7)

    # Hình trên: 4 ngày/nến; thân Q1–Q3, vạch trung vị trắng như video vừa gửi.
    so_nen = int(np.ceil(so_ngay / 4))
    nen = tren.bar(np.zeros(so_nen), np.zeros(so_nen), edgecolor='none', zorder=3)
    rau = [tren.plot([], [], lw=1.3, solid_capstyle='butt', zorder=2)[0] for _ in nen]
    ngang = [tren.plot([], [], color='white', lw=1.4,
                      solid_capstyle='butt', zorder=4)[0] for _ in nen]

    # Hình dưới: khoảng giá từng ngày và đường giá đóng cửa đổi màu.
    duong_thap, = duoi.plot([], [], color='darkgoldenrod', lw=1.1, zorder=2)
    duong_cao, = duoi.plot([], [], color='olivedrab', lw=1.1, zorder=2)
    duong_dong, = duoi.plot([], [], lw=1.4, zorder=3)
    duong_max, = duoi.plot([], [], color='green', lw=0.8, ls=(0, (3, 2)), zorder=0)
    duong_min, = duoi.plot([], [], color='red', lw=0.8, ls=(0, (3, 2)), zorder=0)
    duong_hien_tai, = duoi.plot([], [], color='gray', lw=0.7, ls=':', alpha=0.8, zorder=0)
    nhan_max = duoi.annotate('', (0, 0), xytext=(0, -2), textcoords='offset points',
                            color='green', va='top', clip_on=True)
    nhan_min = duoi.annotate('', (0, 0), xytext=(0, -2), textcoords='offset points',
                            color='red', va='top', clip_on=True)
    nhan_dong = duoi.annotate('', (0, 0), xytext=(0, 2), textcoords='offset points',
                             va='bottom', clip_on=True)
    vung_gia = None

    # Một khung mỗi ngày, thêm khung đầu/cuối; FFmpeg xuất thành video 30 fps.
    thoi_luong = 5663 / 30  # 3 phút 08,77 giây.
    writer = FFMpegWriter(fps=(so_ngay + 2) / thoi_luong, codec='libx264',
                         extra_args=['-r', '30', '-t', str(thoi_luong), '-preset', 'fast',
                                     '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'])
    with writer.saving(fig, str(tep_video), dpi=100):
        writer.grab_frame()
        for i in range(so_ngay):
            k = i // 4
            dau = k * 4
            da_co = gia[dau:i + 1]  # Đủ 28 giá khi nhóm có đủ 4 ngày.
            q1, trung_vi, q3 = np.percentile(da_co, [25, 50, 75])
            x, so_ngay_nhom = (dau + i) / 2, i - dau + 1
            rong = 0.92 * so_ngay_nhom  # Chừa khe 8% giữa các nến.
            mau = mau_gia(dong[i], tham_chieu[i])
            nen[k].set(x=x - rong / 2, y=q1, width=rong, height=q3 - q1, facecolor=mau)
            rau[k].set_data([x, x], [da_co.min(), da_co.max()])
            rau[k].set_color(mau)
            ngang[k].set_data([x - 0.4 * so_ngay_nhom, x + 0.4 * so_ngay_nhom],
                              [trung_vi, trung_vi])

            n = i + 1
            duong_thap.set_data(ngay[:n], thap[:n])
            duong_cao.set_data(ngay[:n], cao[:n])
            duong_dong.set_data(ngay[:n], dong[:n])
            duong_dong.set_color(mau)
            if vung_gia is not None:
                vung_gia.remove()
            vung_gia = duoi.fill_between(ngay[:n], thap[:n], cao[:n],
                                         color='yellow', alpha=0.28, edgecolor='none', zorder=1)
            min_da_co, max_da_co = min(min_da_co, dong[i]), max(max_da_co, dong[i])
            for duong, nhan, muc in [(duong_min, nhan_min, min_da_co),
                                     (duong_max, nhan_max, max_da_co)]:
                duong.set_data([0, so_ngay - 1], [muc, muc])
                nhan.xy = (so_ngay + 5, muc)
                nhan.set_text(f'{muc:,.0f}')
            gan_nhau = (max_da_co - min_da_co) * duoi.bbox.height / (1.1 * gioi_han) < 30
            nhan_max.set_va('bottom' if gan_nhau else 'top')
            nhan_max.set_position((0, 2 if gan_nhau else -2))
            duong_hien_tai.set_data([0, so_ngay - 1], [dong[i], dong[i]])
            nhan_dong.xy = (min(i + 4, so_ngay + 2), dong[i])
            nhan_dong.set(text=f'{dong[i]:,.0f}', color=mau,
                          ha='right' if i > so_ngay - 17 else 'left')
            writer.grab_frame()
            if n % 60 == 0:
                print(f'Da xuat {n}/{so_ngay} ngay', flush=True)
        writer.grab_frame()
    plt.close(fig)
    print(f'Da luu video: {tep_video}')


if __name__ == '__main__':
    gia = pd.read_csv(THU_MUC / 'data/abc-15.csv', header=None).to_numpy(dtype=float)
    if gia.shape != (365, 7) or not np.isfinite(gia).all() or (gia <= 0).any():
        raise ValueError('Du lieu phai gom 365 dong x 7 cot gia hop le.')
    tao_video(gia)
