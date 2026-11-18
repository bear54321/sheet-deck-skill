"""用 Blender 把 3D 模型轉成網頁用的小檔 GLB：減面、縮小貼圖、JPEG 貼圖。

用法（不開視窗，背景執行）：
  /Applications/Blender.app/Contents/MacOS/Blender -b --python optimize_model.py -- 輸入檔 輸出.glb [最多面數] [貼圖最大邊長]
  輸入檔可以是 .glb / .gltf / .fbx / .obj
  最多面數預設 60000（0 = 不減面）；貼圖最大邊長預設 2048
範例：
  Blender -b --python optimize_model.py -- vase.glb 3d/vase.glb 0 2048
  Blender -b --python optimize_model.py -- parrot.fbx 3d/parrot.glb 40000 1024
有骨架動畫的角色（FBX/GLB）會保留動畫；減面可能讓蒙皮變形，角色建議面數不要壓太低。
"""
import bpy, sys, os

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if len(argv) < 2:
    raise SystemExit(__doc__)
src, out = argv[0], argv[1]
max_tris = int(argv[2]) if len(argv) > 2 else 60000
max_tex = int(argv[3]) if len(argv) > 3 else 2048

bpy.ops.wm.read_factory_settings(use_empty=True)
ext = os.path.splitext(src)[1].lower()
if ext in ('.glb', '.gltf'):
    bpy.ops.import_scene.gltf(filepath=src)
elif ext == '.fbx':
    bpy.ops.import_scene.fbx(filepath=src)
elif ext == '.obj':
    bpy.ops.wm.obj_import(filepath=src)
else:
    raise SystemExit('不支援的格式：' + ext)

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
print('[optimize] 原始面數', tris)
if max_tris and tris > max_tris:
    ratio = max_tris / tris
    for o in meshes:
        m = o.modifiers.new('Decimate', 'DECIMATE'); m.ratio = ratio
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.modifier_apply(modifier=m.name)
        o.select_set(False)
    print('[optimize] 減面比例 %.3f' % ratio)

for img in bpy.data.images:
    w, h = img.size
    if w and h and max(w, h) > max_tex:
        k = max_tex / max(w, h)
        img.scale(max(1, int(w * k)), max(1, int(h * k)))
        print('[optimize] 貼圖', img.name, (w, h), '→', tuple(img.size))

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=88, export_animations=True)
print('[optimize] 已輸出 %s（%.1f MB）' % (out, os.path.getsize(out) / 1048576))
