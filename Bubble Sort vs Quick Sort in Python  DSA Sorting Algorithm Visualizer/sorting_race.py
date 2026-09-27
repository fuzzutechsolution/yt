import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import sys

def generate_sorting_data(num_elements=1000):
    """
    Simulates Bubble Sort and Quick Sort on 1,000 elements,
    capturing key snapshot frames for a 9:16 vertical video race.
    """
    np.random.seed(42)
    initial_array = np.random.randint(10, 1000, size=num_elements)
    
    # 1. Bubble Sort Snapshots
    def get_bubble_sort_frames(arr):
        a = arr.copy()
        n = len(a)
        frames = []
        frames.append((a.copy(), 0.0, False, 0)) # (array, progress_pct, is_done, operations)
        
        total_expected_ops = (n * (n - 1)) // 2 # ~499,500 ops
        ops = 0
        
        # Sample 75 frames for ultra-fast rendering (< 4 seconds total)
        target_frames = 75
        step_interval = max(1, total_expected_ops // target_frames)
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                ops += 1
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swapped = True
                
                if ops % step_interval == 0:
                    pct = (ops / total_expected_ops) * 100
                    frames.append((a.copy(), pct, False, ops))
            if not swapped:
                break
                
        frames.append((a.copy(), 100.0, True, ops))
        return frames

    # 2. Quick Sort Snapshots
    def get_quick_sort_frames(arr):
        a = arr.copy()
        frames = []
        ops = [0]
        
        frames.append((a.copy(), 0.0, False, 0))
        
        def quick_sort_rec(low, high):
            if low < high:
                pivot_idx = partition(low, high)
                quick_sort_rec(low, pivot_idx - 1)
                quick_sort_rec(pivot_idx + 1, high)
                
        def partition(low, high):
            pivot = a[high]
            i = low - 1
            for j in range(low, high):
                ops[0] += 1
                if ops[0] % 120 == 0:
                    pct = min(99.0, (ops[0] / 10000) * 100)
                    frames.append((a.copy(), pct, False, ops[0]))
                if a[j] < pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]
            a[i + 1], a[high] = a[high], a[i + 1]
            return i + 1

        quick_sort_rec(0, len(a) - 1)
        frames.append((a.copy(), 100.0, True, ops[0]))
        return frames

    print("Sorting 1,000 elements...", flush=True)
    b_frames = get_bubble_sort_frames(initial_array)
    q_frames = get_quick_sort_frames(initial_array)
    print(f"Captured {len(b_frames)} Bubble Sort frames and {len(q_frames)} Quick Sort frames.", flush=True)
    return initial_array, b_frames, q_frames

def build_race_animation(num_elements=1000, output_mp4="bubble_vs_quick_short.mp4", live_preview=False):
    initial_array, bubble_frames, quick_frames = generate_sorting_data(num_elements)
    
    # 90 total frames (3 seconds at 30 FPS - fast & smooth)
    total_frames = 90

    # Create 9:16 Vertical Figure layout (1080x1920 aspect ratio)
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 16), dpi=100, facecolor='#0F172A')
    
    # Subplots grid: Header (top), Bubble (middle-top), Quick (middle-bottom)
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 4.5, 4.5], hspace=0.35, left=0.08, right=0.92, top=0.94, bottom=0.04)

    ax_head = fig.add_subplot(gs[0])
    ax_bubble = fig.add_subplot(gs[1])
    ax_quick = fig.add_subplot(gs[2])

    for ax in [ax_head, ax_bubble, ax_quick]:
        ax.set_facecolor('#0F172A')

    # Brand & Title Header
    ax_head.axis('off')
    ax_head.text(0.5, 0.85, "FUZZUTECH", fontsize=16, fontweight='bold', color='#38BDF8', ha='center', va='center')
    ax_head.text(0.5, 0.52, "BUBBLE SORT  vs  QUICK SORT", fontsize=20, fontweight='heavy', color='#F8FAFC', ha='center', va='center')
    ax_head.text(0.5, 0.20, "RACE FOR 1,000 ELEMENTS", fontsize=13, fontweight='bold', color='#94A3B8', ha='center', va='center')

    # Setup Subplot 1: Bubble Sort
    ax_bubble.set_title("BUBBLE SORT  |  O(n^2)", fontsize=16, fontweight='bold', color='#FF007F', pad=10, loc='left')
    ax_bubble.set_xlim(0, num_elements)
    ax_bubble.set_ylim(0, 1050)
    ax_bubble.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax_bubble.spines.values():
        spine.set_color('#334155')
        spine.set_linewidth(1.5)

    # Setup Subplot 2: Quick Sort
    ax_quick.set_title("QUICK SORT  |  O(n log n)", fontsize=16, fontweight='bold', color='#10B981', pad=10, loc='left')
    ax_quick.set_xlim(0, num_elements)
    ax_quick.set_ylim(0, 1050)
    ax_quick.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax_quick.spines.values():
        spine.set_color('#334155')
        spine.set_linewidth(1.5)

    # Initial bar charts
    x_indices = np.arange(num_elements)
    bars_b = ax_bubble.bar(x_indices, initial_array, width=1.0, color='#FF007F', edgecolor='none')
    bars_q = ax_quick.bar(x_indices, initial_array, width=1.0, color='#10B981', edgecolor='none')

    # Status Overlay Badges
    badge_b = ax_bubble.text(0.96, 0.88, "Progress: 0.0%\nOps: 0", transform=ax_bubble.transAxes,
                             fontsize=12, fontweight='bold', color='#F8FAFC', ha='right', va='top',
                             bbox=dict(boxstyle='round,pad=0.5', facecolor='#1E293B', alpha=0.9, edgecolor='#FF007F'))

    badge_q = ax_quick.text(0.96, 0.88, "Progress: 0.0%\nOps: 0", transform=ax_quick.transAxes,
                             fontsize=12, fontweight='bold', color='#F8FAFC', ha='right', va='top',
                             bbox=dict(boxstyle='round,pad=0.5', facecolor='#1E293B', alpha=0.9, edgecolor='#10B981'))

    # Quick Sort Finish Banner
    winner_banner = ax_quick.text(0.5, 0.5, "QUICK SORT WINS!\n~250x FASTER THAN BUBBLE SORT",
                                  transform=ax_quick.transAxes, fontsize=18, fontweight='heavy',
                                  color='#6EE7B7', ha='center', va='center',
                                  bbox=dict(boxstyle='round,pad=0.6', facecolor='#064E3B', alpha=0.95, edgecolor='#10B981'))
    winner_banner.set_visible(False)

    def update(frame_idx):
        b_idx = min(int((frame_idx / total_frames) * len(bubble_frames)), len(bubble_frames) - 1)
        q_idx = min(int((frame_idx / total_frames) * len(quick_frames)), len(quick_frames) - 1)

        # Update Bubble Sort
        b_arr, b_pct, b_done, b_ops = bubble_frames[b_idx]
        for bar, h in zip(bars_b, b_arr):
            bar.set_height(h)
        if b_done:
            badge_b.set_text(f"FINISHED!\nOps: {b_ops:,}")
            badge_b.get_bbox_patch().set_edgecolor('#10B981')
            for bar in bars_b:
                bar.set_color('#10B981')
        else:
            badge_b.set_text(f"Progress: {b_pct:.1f}%\nOps: {b_ops:,}")

        # Update Quick Sort
        q_arr, q_pct, q_done, q_ops = quick_frames[q_idx]
        for bar, h in zip(bars_q, q_arr):
            bar.set_height(h)
        if q_done or q_idx == len(quick_frames) - 1:
            badge_q.set_text(f"FINISHED!\nOps: {q_ops:,}")
            badge_q.get_bbox_patch().set_edgecolor('#10B981')
            for bar in bars_q:
                bar.set_color('#10B981')
            winner_banner.set_visible(True)
        else:
            badge_q.set_text(f"Progress: {q_pct:.1f}%\nOps: {q_ops:,}")

        return list(bars_b) + list(bars_q) + [badge_b, badge_q, winner_banner]

    if live_preview:
        print("Launching Live Animation Preview...", flush=True)
        anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=30, blit=False, repeat=True)
        plt.show()
    else:
        print(f"Rendering 9:16 vertical video output to '{output_mp4}'...", flush=True)
        anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=30, blit=False)
        
        # Use quiet FFmpeg flags to avoid VS Code Code Runner stderr warnings
        writer = animation.FFMpegWriter(fps=30, metadata=dict(artist='FuzzuTech'), bitrate=4000, extra_args=['-loglevel', 'error'])
        anim.save(output_mp4, writer=writer)
        plt.close(fig)
        print(f"[SUCCESS] Video rendering complete! Saved to '{output_mp4}'.", flush=True)

if __name__ == "__main__":
    preview = "--live" in sys.argv
    build_race_animation(num_elements=1000, output_mp4="bubble_vs_quick_short.mp4", live_preview=preview)
