"use client"
import React from 'react';
import Cropper from 'react-easy-crop';
import { Area } from 'react-easy-crop';
import { Button, Input, Box } from '@chakra-ui/react';

import { useUpdatePhotoMutation } from '@/app/store/apis/usersApi';

import { getCroppedImg } from '@/app/utils/operationsWithImages'; // Utility to get the cropped image

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

type Props = {
    id: string,
    setIsCropping: (value: boolean) => void
}

const ImageUploader = ({id, setIsCropping}: Props) => {
  const { t } = usePrefixedTranslation("Components.ImageUploader")

  const [photo, setPhoto] = React.useState<string | null>(null);
//   const [photo, setPhoto] = React.useState<string>("");
  const [crop, setCrop] = React.useState({ x: 0, y: 0 });
  const [zoom, setZoom] = React.useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = React.useState<Area | null>(null);
  const [file, setFile] = React.useState<File | null>(null);

  const [updatePhoto, {data: response, isSuccess: isPhotoChangeSuccessful, isLoading: isPhotoLoading}] = useUpdatePhotoMutation();

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        setIsCropping(true);
        setFile(e.target.files[0]);
        const reader = new FileReader();
        reader.onload = (event) => setPhoto(event.target?.result as string);
        reader.readAsDataURL(e.target.files[0]);
    }
};

const onCropComplete = (_croppedArea: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
};

const handleCrop = async () => {
    if (!photo || !croppedAreaPixels) {
        console.error('Photo or cropped area is missing');
        return;
    }

    try {
        const croppedImage = await getCroppedImg(photo, croppedAreaPixels);
        if (!croppedImage) {
        console.error('Cropped image is null');
        return;
        }

        const formData = new FormData();
        // formData.append('photo', croppedImage, file?.name || `${id}.jpg`);
        formData.append('photo', croppedImage, `${id}.jpg`);
        await updatePhoto({ id, formData });
        setIsCropping(false)
    } catch (error) {
        console.error('Error cropping image:', error);
    }
};

const handleDecline = async () => {
    // setPhoto(null);
    setIsCropping(false);
}

  return (
    <>
      <Input type="file" accept="image/*" onChange={handlePhotoChange} />
      {photo && (
        <Box
          position="fixed"
          top="0"
          left="0"
          width="100vw"
          height="100vh"
          zIndex="999"
          backgroundColor="rgba(0, 0, 0, 0.8)"
          display="flex"
          flexDirection="column"
          justifyContent="center"
          alignItems="center"
        >
          <Box width={{ base: '90vw', md: '500px' }} height={{ base: '90vh', md: '500px' }}>
            <Cropper
              image={photo}
              crop={crop}
              zoom={zoom}
              aspect={1} 
              onCropChange={setCrop}
              onZoomChange={setZoom}
              onCropComplete={onCropComplete}
              objectFit="contain" // Fit the cropper to the screen
            />
          </Box>
          <Button colorScheme="teal" mt={4} onClick={handleCrop}>
            {t("cropAndUploadLabel")}
          </Button>
          <Button colorScheme="teal" mt={4} onClick={handleDecline}>
            {t("declineLabel")}
          </Button>
        </Box>
      )}
    </>
  );
};


export default ImageUploader;