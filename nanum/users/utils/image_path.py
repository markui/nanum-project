__all__ = (
    'user_img_path',
    'user_thumb_img_200_path',
    'user_thumb_img_50_path',
    'user_thumb_img_25_path',
)


def user_img_path(instance, filename):
    # 업로드 이미지 file 저장 경로
    return f'profile/img/{instance.user.__str__()}/{filename}'


def user_thumb_img_200_path(instance, filename):
    # 200 * 200 썸네일 이미지 file 저장 경로
    return f'profile/thumbnail_img_200/{instance.user.__str__()}/{filename}'


def user_thumb_img_50_path(instance, filename):
    # 50 * 50 썸네일 이미지 file 저장 경로
    return f'profile/thumbnail_img_50/{instance.user.__str__()}/{filename}'


def user_thumb_img_25_path(instance, filename):
    # 25 * 25 썸네일 이미지 file 저장 경로
    return f'profile/thumbnail_img_25/{instance.user.__str__()}/{filename}'