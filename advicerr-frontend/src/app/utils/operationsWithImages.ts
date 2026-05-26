export type Area = {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  
export async function getCroppedImg(imageSrc: string, crop: Area): Promise<Blob | null> {
    const image = await createImage(imageSrc);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
        throw new Error('Failed to get canvas context');
    }

    canvas.width = crop.width;
    canvas.height = crop.height;

    ctx.drawImage(
        image,
        crop.x,
        crop.y,
        crop.width,
        crop.height,
        0,
        0,
        crop.width,
        crop.height
    );

    return new Promise<Blob | null>((resolve) => {
        canvas.toBlob((blob) => {
        resolve(blob);
        }, 'image/jpeg');
    });
}

export function createImage(url: string): Promise<HTMLImageElement> {
    return new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.src = url;
        img.onload = () => resolve(img);
        img.onerror = (error) => reject(error);
    });
}
  