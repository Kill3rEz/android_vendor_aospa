#
# SPDX-FileCopyrightText: Paranoid Android
# SPDX-License-Identifier: Apache-2.0
#

ifeq (aospa_phone2,$(TARGET_PRODUCT))

# CAS
TARGET_REQUIRES_HIDL_CAS_HAL := false

# The 6.12 display HAL can't convert sRGB layers to P3 on its pipes, and its GPU fallback
# hides translucent layers such as the photo picker, so keep the panel in sRGB
TARGET_HAS_WIDE_COLOR_DISPLAY := false

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base_telephony.mk)

# Inherit from the device configuration.
$(call inherit-product, device/nothing/phone2/device.mk)

# Inherit from the AOSPA configuration.
$(call inherit-product, vendor/aospa/target/product/aospa-target.mk)

PRODUCT_BRAND := Nothing
PRODUCT_DEVICE := phone2
PRODUCT_MANUFACTURER := Nothing
PRODUCT_MODEL := A065
PRODUCT_NAME := aospa_phone2

# Bootanimation resolution
TARGET_BOOT_ANIMATION_RES := 1080

TARGET_USES_BLUR := true

# Override device name for Play Store.
PRODUCT_BUILD_PROP_OVERRIDES += \
    DeviceName=Pong \
    DeviceProduct=Pong \
    SystemDevice=Pong \
    SystemName=Pong

PRODUCT_GMS_CLIENTID_BASE := android-nothing

endif
