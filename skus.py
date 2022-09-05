"""
Constants for the different SKUs in the CloudCIX iaas system
"""

DEFAULT = 'SKU_Not_Available'

# Image SKUs
CENTOS_6 = 'CentOS6'
CENTOS_7 = 'CentOS7'
PHANTOM = 'Phantom'
UBUNTU_12 = 'Ubuntu1204LTS'
UBUNTU_DESKTOP_12 = 'UbuntuDtop1204LTS'
UBUNTU_14 = 'Ubuntu1404LTS'
UBUNTU_16 = 'Ubuntu1604LTS'
UBUNTU_18 = 'Ubuntu1804LTS'
WINDOWS_2003 = 'MSServer2003'
WINDOWS_2008 = 'MSServer2008'
WINDOWS_2012 = 'MSServer2012'
WINDOWS_2016 = 'MSServer2016'
WINDOWS_2019 = 'MSServer2019'
REDHAT_7 = 'MCT2561'
CENTOS_8 = 'CentOS8'
UBUNTU_20 = 'Ubuntu2004LTS'
ROCKY_84 = 'ROCKY84'
ROCKY_85 = 'ROCKY85'

# Storage SKUs
HDD_001 = 'HDD_001'
SSD_001 = 'SSD_001'

# VM SKUs
NAT_001 = 'NAT_001'
RAM_001 = 'RAM_001'
VCPU_001 = 'vCPU_001'

# VPN SKUs
SITE_TO_SITE = 'VPNS2S'
DYNAMIC_SECURE_CONNECT = 'VPNDSC'

IMAGE_SKU_MAP = {
    2: WINDOWS_2012,
    3: WINDOWS_2016,
    4: WINDOWS_2008,
    5: WINDOWS_2003,
    6: UBUNTU_16,
    7: UBUNTU_14,
    8: UBUNTU_12,
    9: UBUNTU_DESKTOP_12,
    10: CENTOS_7,
    11: CENTOS_6,
    12: UBUNTU_18,
    13: WINDOWS_2019,
    14: PHANTOM,
    15: REDHAT_7,
    16: CENTOS_8,
    17: UBUNTU_20,
    18: ROCKY_84,
    19: ROCKY_85,
}

STORAGE_SKU_MAP = {
    1: HDD_001,
    2: SSD_001,
}
