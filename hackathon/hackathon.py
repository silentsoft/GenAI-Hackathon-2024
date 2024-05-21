import os

import numpy as np
from PIL import Image, ImageChops
import pillow_avif
from skimage.measure import label, regionprops
from skimage.metrics import structural_similarity
from skimage.transform import resize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import OverlapInfo, NonOverlapInfo


def compress_image_through_avif(input_path):
    with Image.open(input_path) as image:
        if image.format.upper() == 'AVIF':
            return input_path

        output_path = f"{input_path}.avif"
        image.save(output_path, format="AVIF")
        return output_path


def calculate_image_similarity(image1, image2):
    # 이미지를 회색조로 변환하고, 동일한 크기로 조정
    image1_gray = np.array(image1.convert('L'))
    image2_gray = np.array(image2.convert('L'))

    # 이미지 크기 조정
    image1_gray = resize(image1_gray, (256, 256), anti_aliasing=True)
    image2_gray = resize(image2_gray, (256, 256), anti_aliasing=True)

    # SSIM 계산
    score, _ = structural_similarity(image1_gray, image2_gray, full=True, data_range=image1_gray.max() - image1_gray.min())
    return score


def find_and_save_regions(image_paths, db_path, output_dir):
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # 이미지를 AVIF로 압축하고 RGB로 변환
    images = [Image.open(compress_image_through_avif(path)).convert('RGB') for path in image_paths]
    num_images = len(images)

    # 모든 이미지 쌍에 대해 차이 계산
    diff_accumulated = None
    for i in range(num_images):
        for j in range(i + 1, num_images):
            diff = ImageChops.difference(images[i], images[j])
            if diff_accumulated is None:
                diff_accumulated = diff
            else:
                diff_accumulated = ImageChops.add(diff_accumulated, diff)

    # 차이점을 기준으로 중복 영역을 찾기 위한 이진화
    diff_gray = diff_accumulated.convert('L')
    diff_np = np.array(diff_gray)
    binary_diff = (diff_np > 30).astype(np.uint8) * 255

    # 차이점의 반전 (중복 영역)
    inverse_binary_diff = np.invert(binary_diff)

    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    saved_images = []

    labeled_array, num_features = label(inverse_binary_diff, connectivity=2, return_num=True)
    regions = regionprops(labeled_array)
    for i, region in enumerate(regions, start=1):
        if region.area > 4:  # 최소 영역 크기 조건
            minr, minc, maxr, maxc = region.bbox
            mask = (labeled_array[minr:maxr, minc:maxc] == region.label).astype(np.uint8) * 255
            mask = Image.fromarray(mask, mode='L')

            for img_index, img in enumerate(images):
                overlap_part = Image.composite(img.crop((minc, minr, maxc, maxr)), Image.new('RGB', (maxc - minc, maxr - minr)), mask)
                is_saved = False
                for saved_image_info in saved_images:
                    saved_image = Image.open(saved_image_info['filename'])
                    similarity = calculate_image_similarity(overlap_part, saved_image)
                    if similarity > 0.95:  # 유사도가 95% 이상이면 동일한 이미지로 간주
                        session.add(OverlapInfo(
                            image_index=img_index + 1,
                            region_id=i,
                            bbox_minr=minr,
                            bbox_minc=minc,
                            bbox_maxr=maxr,
                            bbox_maxc=maxc,
                            overlap_image=saved_image_info['filename']
                        ))
                        is_saved = True
                        break

                if not is_saved:
                    overlap_filename = os.path.join(output_dir, f'overlap_image{img_index + 1}_{i}.avif')
                    overlap_part.save(overlap_filename)
                    saved_images.append({
                        "filename": overlap_filename,
                        "region_id": i
                    })
                    session.add(OverlapInfo(
                        image_index=img_index + 1,
                        region_id=i,
                        bbox_minr=minr,
                        bbox_minc=minc,
                        bbox_maxr=maxr,
                        bbox_maxc=maxc,
                        overlap_image=overlap_filename
                    ))

    # 각 이미지별로 중복되지 않은 부분 추출 및 저장
    for img_index, img in enumerate(images):
        labeled_array, num_features = label(binary_diff, connectivity=2, return_num=True)
        regions = regionprops(labeled_array)
        region_counter = 1

        for region in regions:
            if region.area > 4:  # 최소 영역 크기 조건
                minr, minc, maxr, maxc = region.bbox
                mask = (labeled_array[minr:maxr, minc:maxc] == region.label).astype(np.uint8) * 255
                mask = Image.fromarray(mask, mode='L')

                non_overlap_part = Image.composite(img.crop((minc, minr, maxc, maxr)), Image.new('RGB', (maxc - minc, maxr - minr)), mask)
                is_saved = False
                for saved_image_info in saved_images:
                    saved_image = Image.open(saved_image_info['filename'])
                    similarity = calculate_image_similarity(non_overlap_part, saved_image)
                    if similarity > 0.95:  # 유사도가 95% 이상이면 동일한 이미지로 간주
                        session.add(NonOverlapInfo(
                            image_index=img_index + 1,
                            region_id=region_counter,
                            bbox_minr=minr,
                            bbox_minc=minc,
                            bbox_maxr=maxr,
                            bbox_maxc=maxc,
                            non_overlap_image=saved_image_info['filename']
                        ))
                        is_saved = True
                        break

                if not is_saved:
                    non_overlap_filename = os.path.join(output_dir, f'non_overlap_image{img_index + 1}_{region_counter}.avif')
                    non_overlap_part.save(non_overlap_filename)
                    saved_images.append({
                        "filename": non_overlap_filename,
                        "region_id": region_counter
                    })
                    session.add(NonOverlapInfo(
                        image_index=img_index + 1,
                        region_id=region_counter,
                        bbox_minr=minr,
                        bbox_minc=minc,
                        bbox_maxr=maxr,
                        bbox_maxc=maxc,
                        non_overlap_image=non_overlap_filename
                    ))

                region_counter += 1

    session.commit()


def reconstruct_image(image_index, db_path, output_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    overlap_infos = session.query(OverlapInfo).filter_by(image_index=image_index).all()
    non_overlap_infos = session.query(NonOverlapInfo).filter_by(image_index=image_index).all()

    max_width = max([info.bbox_maxc for info in overlap_infos + non_overlap_infos])
    max_height = max([info.bbox_maxr for info in overlap_infos + non_overlap_infos])

    reconstructed_image = Image.new('RGB', (max_width, max_height))

    for info in overlap_infos:
        bbox = (info.bbox_minc, info.bbox_minr, info.bbox_maxc, info.bbox_maxr)
        overlap_image = Image.open(info.overlap_image)
        reconstructed_image.paste(overlap_image, (info.bbox_minc, info.bbox_minr))

    for info in non_overlap_infos:
        bbox = (info.bbox_minc, info.bbox_minr, info.bbox_maxc, info.bbox_maxr)
        non_overlap_image = Image.open(info.non_overlap_image)
        reconstructed_image.paste(non_overlap_image, (info.bbox_minc, info.bbox_minr))

    reconstructed_image.save(output_path)
