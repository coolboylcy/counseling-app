from PIL import Image
import os

def process_image(input_path, output_path):
    # 打开图片
    img = Image.open(input_path)
    
    # 获取图片尺寸
    width, height = img.size
    
    # 计算裁剪区域（假设二维码在图片中心，占据80%的区域）
    crop_width = int(width * 0.8)
    crop_height = int(height * 0.8)
    
    # 计算裁剪的起始点（居中裁剪）
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height
    
    # 裁剪图片
    img_cropped = img.crop((left, top, right, bottom))
    
    # 保存处理后的图片
    img_cropped.save(output_path, quality=95)
    print(f"Processed {input_path} -> {output_path}")

def main():
    # 确保输出目录存在
    if not os.path.exists('static/images/processed'):
        os.makedirs('static/images/processed')
    
    # 处理微信支付二维码
    process_image(
        'static/images/wechat-qr.jpg',
        'static/images/processed/wechat-qr.jpg'
    )
    
    # 处理支付宝二维码
    process_image(
        'static/images/alipay-qr.jpg',
        'static/images/processed/alipay-qr.jpg'
    )

if __name__ == '__main__':
    main() 