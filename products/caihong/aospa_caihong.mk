#
# SPDX-FileCopyrightText: Paranoid Android
# SPDX-License-Identifier: Apache-2.0
#

ifeq (aospa_caihong,$(TARGET_PRODUCT))

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/large_screen_common.mk)

# Inherit from the caihong device.
$(call inherit-product, device/oneplus/caihong/device.mk)

# Inherit from the AOSPA configuration.
$(call inherit-product, vendor/aospa/target/product/aospa-target.mk)

PRODUCT_NAME := aospa_caihong
PRODUCT_DEVICE := caihong
PRODUCT_MANUFACTURER := OnePlus
PRODUCT_BRAND := OnePlus
PRODUCT_MODEL := OPD2403
PRODUCT_CHARACTERISTICS := nosdcard,tablet

PRODUCT_GMS_CLIENTID_BASE := android-oneplus

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="qssi_64-user 16 BP2A.250605.015 1778208015618 release-keys" \
    BuildFingerprint=OnePlus/OPD2403IN/OP5DAAL1:16/UKQ1.231108.001/U.R4T3.367361a-12b9c76-12b9c73:user/release-keys \
    DeviceName=OP5DAAL1 \
    DeviceProduct=OPD2403 \
    SystemDevice=OP5DAAL1 \
    SystemName=OPD2403

# Boot animation resolution.
TARGET_BOOT_ANIMATION_RES := 1440

TARGET_USES_BLUR := true

endif
