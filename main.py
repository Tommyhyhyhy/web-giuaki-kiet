import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter


def mau_gia(gia, tham_chieu):
    """Chọn màu theo giá đóng cửa ngày trước, đúng quy ước đề bài."""
    if np.isclose(gia, 0.9 * tham_chieu, rtol=0, atol=1e-5):
        return 'dodgerblue'
    if np.isclose(gia, 1.1 * tham_chieu, rtol=0, atol=1e-5):
        return 'mediumorchid'
    if np.isclose(gia, tham_chieu, rtol=0, atol=1e-5):
        return 'yellow'
    return 'limegreen' if gia > tham_chieu else 'red'


def tao_video(gia, tep_video='static/video/abc15.mp4'):
    plt.switch_backend('Agg')
    plt.style.use('dark_background')
    plt.rcParams['animation.ffmpeg_path'] = 'tools/ffmpeg.exe'

    so_ngay = len(gia)
    ngay = np.arange(1, so_ngay + 1)
    thap, cao = gia.min(axis=1), gia.max(axis=1)
    dong = gia[:, -1]
    tham_chieu = np.r_[10000, dong[:-1]]  # Ngày đầu giả định là 10.000.

    # Chia mỗi 30 ngày thành 8 nhóm (mỗi nến gộp 3 hoặc 4 ngày).
    nhom_nen = []
    for dau in range(0, so_ngay, 30):
        nhom = np.arange(dau, min(dau + 30, so_ngay))
        nhom_nen.extend(np.array_split(nhom, int(np.ceil(len(nhom) * 8 / 30))))

    fig, (tren, duoi) = plt.subplots(2, 1, figsize=(14, 7.5), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.98, hspace=0.08)
    gioi_han = np.ceil(cao.max() / 5000) * 5000
    for ax in (tren, duoi):
        ax.set_xlim(-5, so_ngay + 35)
        ax.set_ylim(0, gioi_han)
        ax.set_ylabel('Giá', fontweight='bold')
        ax.set_xticks(np.arange(0, so_ngay + 1, 30))
        ax.yaxis.set_major_formatter('{x:,.0f}')
    duoi.set_xlabel('Ngày', fontweight='bold')

    # Hình dưới: toàn bộ đường và vùng giá sáng theo màu nến hiện tại.
    duong_thap, = duoi.plot([], [], linewidth=1.5)
    duong_cao, = duoi.plot([], [], linewidth=1.5)
    vung_gia = None
    # Hai mốc xuất phát cùng giá đầu tiên, chỉ mở rộng theo dữ liệu đã hiện.
    min_da_co = max_da_co = float(gia[0, 0])
    duong_max = duoi.axhline(max_da_co, color='green', linestyle=(0, (5, 5)),
                             linewidth=0.8, alpha=0.7)
    duong_min = duoi.axhline(min_da_co, color='red', linestyle=(5, (5, 5)),
                             linewidth=0.8, alpha=0.7)
    nhan_max = duoi.text(so_ngay + 2, max_da_co, f'{max_da_co:,.0f}',
                         color='green', va='bottom')
    nhan_min = duoi.text(so_ngay + 2, min_da_co, f'{min_da_co:,.0f}',
                         color='red', va='top')
    duong_dong = duoi.axhline(min_da_co, linewidth=1, alpha=0.7, visible=False)
    nhan_dong = duoi.text(so_ngay + 2, min_da_co, '', va='center')

    # Tạo sẵn nến rỗng; cập nhật dần khi video chạy đến từng ngày.
    nen = tren.bar(np.zeros(len(nhom_nen)), np.zeros(len(nhom_nen)), width=2.4)
    rau = [tren.plot([], [], linewidth=1.5)[0] for _ in nhom_nen]
    ngang = [tren.plot([], [], linewidth=1.5)[0] for _ in nhom_nen]

    writer = FFMpegWriter(fps=(so_ngay + 1) / 180, codec='libx264',
                         extra_args=['-pix_fmt', 'yuv420p', '-movflags', '+faststart'])
    with writer.saving(fig, tep_video, dpi=100):
        writer.grab_frame()  # Cho thấy hai mốc trùng nhau trước khi giá biến động.
        duong_dong.set_visible(True)
        for i in range(so_ngay):
            for k, nhom in enumerate(nhom_nen):
                dau = int(nhom[0])
                if dau > i:
                    break
                cuoi = min(int(nhom[-1]), i)
                da_co = gia[dau:cuoi + 1]  # Chỉ dùng các ngày đã xuất hiện.
                mo, dong_nen = da_co[0, 0], da_co[-1, -1]
                x = (dau + cuoi) / 2 + 1
                mau = mau_gia(dong_nen, tham_chieu[cuoi])
                nen[k].set_x(x - 1.2)
                nen[k].set_y(min(mo, dong_nen))
                nen[k].set_height(abs(dong_nen - mo))
                nen[k].set_color(mau)
                rau[k].set_data([x, x], [da_co.min(), da_co.max()])
                rau[k].set_color(mau)
                # Vạch ngang giúp nhìn thấy nến khi mở cửa bằng đóng cửa.
                ngang[k].set_data([x - 1.2, x + 1.2], [dong_nen, dong_nen])
                ngang[k].set_color(mau)

            n = i + 1
            mau = mau_gia(dong[i], tham_chieu[i])
            duong_thap.set_data(ngay[:n], thap[:n])
            duong_cao.set_data(ngay[:n], cao[:n])
            # Chỉ dùng một màu cho toàn bộ phần đã vẽ, không lưu màu nến cũ.
            duong_thap.set_color(mau)
            duong_cao.set_color(mau)
            if vung_gia is not None:
                vung_gia.remove()
            vung_gia = duoi.fill_between(ngay[:n], thap[:n], cao[:n],
                                         color=mau, alpha=0.45)
            min_da_co = min(min_da_co, thap[i])
            max_da_co = max(max_da_co, cao[i])
            for duong, nhan, muc in [(duong_min, nhan_min, min_da_co),
                                     (duong_max, nhan_max, max_da_co)]:
                duong.set_ydata([muc, muc])
                nhan.set_y(muc)
                nhan.set_text(f'{muc:,.0f}')
            duong_dong.set_ydata([dong[i], dong[i]])
            duong_dong.set_color(mau)
            nhan_dong.set_y(dong[i])
            nhan_dong.set_text(f'{dong[i]:,.0f}')
            nhan_dong.set_color(mau)
            writer.grab_frame()
            if n % 60 == 0:
                print(f'Đã xuất {n}/{so_ngay} ngày', flush=True)
    plt.close(fig)
    print(f'Đã lưu video: {tep_video}')


if __name__ == '__main__':
    gia = pd.read_csv('data/abc-15.csv', header=None).to_numpy(dtype=float)
    if gia.shape != (365, 7) or not np.isfinite(gia).all() or (gia <= 0).any():
        raise ValueError('Dữ liệu phải gồm 365 dòng × 7 cột giá hợp lệ.')
    tao_video(gia)
