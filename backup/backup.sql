-- MariaDB dump 10.19  Distrib 10.5.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mbkm_db
-- ------------------------------------------------------
-- Server version	10.5.12-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tbl_berkas_mbkm`
--

DROP TABLE IF EXISTS `tbl_berkas_mbkm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_berkas_mbkm` (
  `id_pengajuan` varchar(50) NOT NULL,
  `sertifikat_program` text NOT NULL,
  `laporan_program` text NOT NULL,
  `hasil_program` text NOT NULL,
  `tanggal_mulai_program` date NOT NULL,
  `tanggal_selesai_program` date NOT NULL,
  `dokumentasi_program` text NOT NULL,
  `status_berkas` enum('Waiting','Rejected','Accepted') NOT NULL DEFAULT 'Waiting',
  PRIMARY KEY (`id_pengajuan`),
  CONSTRAINT `tbl_berkas_mbkm_ibfk_1` FOREIGN KEY (`id_pengajuan`) REFERENCES `tbl_pengajuan_mbkm` (`id_pengajuan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_berkas_mbkm`
--

LOCK TABLES `tbl_berkas_mbkm` WRITE;
/*!40000 ALTER TABLE `tbl_berkas_mbkm` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_berkas_mbkm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_form_assesmen`
--

DROP TABLE IF EXISTS `tbl_form_assesmen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_form_assesmen` (
  `id_assesmen` varchar(50) NOT NULL,
  `nilai_matkul_1` varchar(5) NOT NULL,
  `nilai_matkul_2` varchar(5) DEFAULT NULL,
  `nilai_matkul_3` varchar(5) DEFAULT NULL,
  `nilai_matkul_4` varchar(5) DEFAULT NULL,
  `nilai_matkul_5` varchar(5) DEFAULT NULL,
  `nilai_matkul_6` varchar(5) DEFAULT NULL,
  `nilai_matkul_7` varchar(5) DEFAULT NULL,
  `nilai_matkul_8` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id_assesmen`),
  CONSTRAINT `tbl_form_assesmen_ibfk_1` FOREIGN KEY (`id_assesmen`) REFERENCES `tbl_kegiatan_assesmen` (`id_assesmen`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_form_assesmen`
--

LOCK TABLES `tbl_form_assesmen` WRITE;
/*!40000 ALTER TABLE `tbl_form_assesmen` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_form_assesmen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_kegiatan_assesmen`
--

DROP TABLE IF EXISTS `tbl_kegiatan_assesmen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_kegiatan_assesmen` (
  `id_assesmen` varchar(50) NOT NULL,
  `id_pengajuan` varchar(50) NOT NULL,
  `waktu` datetime NOT NULL,
  `tempat_link` text NOT NULL,
  `status_assesmen` enum('Belum Selesai','Selesai') NOT NULL DEFAULT 'Belum Selesai',
  PRIMARY KEY (`id_assesmen`),
  KEY `id_pengajuan` (`id_pengajuan`),
  CONSTRAINT `tbl_kegiatan_assesmen_ibfk_1` FOREIGN KEY (`id_pengajuan`) REFERENCES `tbl_pengajuan_mbkm` (`id_pengajuan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kegiatan_assesmen`
--

LOCK TABLES `tbl_kegiatan_assesmen` WRITE;
/*!40000 ALTER TABLE `tbl_kegiatan_assesmen` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_kegiatan_assesmen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_mata_kuliah`
--

DROP TABLE IF EXISTS `tbl_mata_kuliah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_mata_kuliah` (
  `kode_matkul` varchar(10) NOT NULL,
  `nama_matkul` varchar(100) NOT NULL,
  `jumlah_sks` int(11) NOT NULL,
  PRIMARY KEY (`kode_matkul`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_mata_kuliah`
--

LOCK TABLES `tbl_mata_kuliah` WRITE;
/*!40000 ALTER TABLE `tbl_mata_kuliah` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_mata_kuliah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_matkul_mbkm`
--

DROP TABLE IF EXISTS `tbl_matkul_mbkm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_matkul_mbkm` (
  `id_pengajuan` varchar(30) NOT NULL,
  `kode_matkul_1` varchar(10) NOT NULL,
  `nomor_dosen_1` varchar(30) NOT NULL,
  `kode_matkul_2` varchar(10) DEFAULT NULL,
  `nomor_dosen_2` varchar(30) DEFAULT NULL,
  `kode_matkul_3` varchar(10) DEFAULT NULL,
  `nomor_dosen_3` varchar(30) DEFAULT NULL,
  `kode_matkul_4` varchar(10) DEFAULT NULL,
  `nomor_dosen_4` varchar(30) DEFAULT NULL,
  `kode_matkul_5` varchar(10) DEFAULT NULL,
  `nomor_dosen_5` varchar(30) DEFAULT NULL,
  `kode_matkul_6` varchar(10) DEFAULT NULL,
  `nomor_dosen_6` varchar(30) DEFAULT NULL,
  `kode_matkul_7` varchar(10) DEFAULT NULL,
  `nomor_dosen_7` varchar(30) DEFAULT NULL,
  `kode_matkul_8` varchar(10) DEFAULT NULL,
  `nomor_dosen_8` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id_pengajuan`),
  KEY `kode_matkul_1` (`kode_matkul_1`),
  KEY `kode_matkul_2` (`kode_matkul_2`),
  KEY `kode_matkul_3` (`kode_matkul_3`),
  KEY `kode_matkul_4` (`kode_matkul_4`),
  KEY `kode_matkul_5` (`kode_matkul_5`),
  KEY `kode_matkul_6` (`kode_matkul_6`),
  KEY `kode_matkul_7` (`kode_matkul_7`),
  KEY `kode_matkul_8` (`kode_matkul_8`),
  KEY `nomor_dosen_1` (`nomor_dosen_1`),
  KEY `nomor_dosen_2` (`nomor_dosen_2`),
  KEY `nomor_dosen_3` (`nomor_dosen_3`),
  KEY `nomor_dosen_4` (`nomor_dosen_4`),
  KEY `nomor_dosen_5` (`nomor_dosen_5`),
  KEY `nomor_dosen_6` (`nomor_dosen_6`),
  KEY `nomor_dosen_7` (`nomor_dosen_7`),
  KEY `nomor_dosen_8` (`nomor_dosen_8`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_1` FOREIGN KEY (`id_pengajuan`) REFERENCES `tbl_pengajuan_mbkm` (`id_pengajuan`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_10` FOREIGN KEY (`nomor_dosen_1`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_11` FOREIGN KEY (`nomor_dosen_2`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_12` FOREIGN KEY (`nomor_dosen_3`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_13` FOREIGN KEY (`nomor_dosen_4`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_14` FOREIGN KEY (`nomor_dosen_5`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_15` FOREIGN KEY (`nomor_dosen_6`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_16` FOREIGN KEY (`nomor_dosen_7`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_17` FOREIGN KEY (`nomor_dosen_8`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_2` FOREIGN KEY (`kode_matkul_1`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_3` FOREIGN KEY (`kode_matkul_2`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_4` FOREIGN KEY (`kode_matkul_3`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_5` FOREIGN KEY (`kode_matkul_4`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_6` FOREIGN KEY (`kode_matkul_5`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_7` FOREIGN KEY (`kode_matkul_6`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_8` FOREIGN KEY (`kode_matkul_7`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`),
  CONSTRAINT `tbl_matkul_mbkm_ibfk_9` FOREIGN KEY (`kode_matkul_8`) REFERENCES `tbl_mata_kuliah` (`kode_matkul`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_matkul_mbkm`
--

LOCK TABLES `tbl_matkul_mbkm` WRITE;
/*!40000 ALTER TABLE `tbl_matkul_mbkm` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_matkul_mbkm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_pengajuan_mbkm`
--

DROP TABLE IF EXISTS `tbl_pengajuan_mbkm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_pengajuan_mbkm` (
  `id_pengajuan` varchar(50) NOT NULL,
  `nomor_induk_mahasiswa` varchar(30) NOT NULL,
  `kode_prodi` varchar(5) NOT NULL,
  `angkatan` int(11) NOT NULL,
  `nama_program` text NOT NULL,
  `jenis_program` text NOT NULL,
  `tempat_program` text NOT NULL,
  `bukti_program` text NOT NULL,
  `semester_klaim` int(11) NOT NULL,
  `status_pengajuan` enum('Waiting','Rejected','Accepted') NOT NULL DEFAULT 'Waiting',
  PRIMARY KEY (`id_pengajuan`),
  KEY `nomor_induk_mahasiswa` (`nomor_induk_mahasiswa`),
  KEY `kode_prodi` (`kode_prodi`),
  CONSTRAINT `tbl_pengajuan_mbkm_ibfk_1` FOREIGN KEY (`nomor_induk_mahasiswa`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_pengajuan_mbkm_ibfk_2` FOREIGN KEY (`kode_prodi`) REFERENCES `tbl_prodi_if` (`kode_prodi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_pengajuan_mbkm`
--

LOCK TABLES `tbl_pengajuan_mbkm` WRITE;
/*!40000 ALTER TABLE `tbl_pengajuan_mbkm` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_pengajuan_mbkm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_peserta_assesmen`
--

DROP TABLE IF EXISTS `tbl_peserta_assesmen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_peserta_assesmen` (
  `id_assesmen` varchar(50) NOT NULL,
  `nomor_mahasiswa` varchar(30) NOT NULL,
  `nomor_dosen_wali` varchar(30) NOT NULL,
  `nomor_kepala_prodi` varchar(30) NOT NULL,
  `nomor_ketua_jurusan` varchar(30) NOT NULL,
  `nomor_dosen_1` varchar(30) NOT NULL,
  `nomor_dosen_2` varchar(30) DEFAULT NULL,
  `nomor_dosen_3` varchar(30) DEFAULT NULL,
  `nomor_dosen_4` varchar(30) DEFAULT NULL,
  `nomor_dosen_5` varchar(30) DEFAULT NULL,
  `nomor_dosen_6` varchar(30) DEFAULT NULL,
  `nomor_dosen_7` varchar(30) DEFAULT NULL,
  `nomor_dosen_8` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id_assesmen`),
  KEY `nomor_mahasiswa` (`nomor_mahasiswa`),
  KEY `nomor_dosen_wali` (`nomor_dosen_wali`),
  KEY `nomor_kepala_prodi` (`nomor_kepala_prodi`),
  KEY `nomor_ketua_jurusan` (`nomor_ketua_jurusan`),
  KEY `nomor_dosen_1` (`nomor_dosen_1`),
  KEY `nomor_dosen_2` (`nomor_dosen_2`),
  KEY `nomor_dosen_3` (`nomor_dosen_3`),
  KEY `nomor_dosen_4` (`nomor_dosen_4`),
  KEY `nomor_dosen_5` (`nomor_dosen_5`),
  KEY `nomor_dosen_6` (`nomor_dosen_6`),
  KEY `nomor_dosen_7` (`nomor_dosen_7`),
  KEY `nomor_dosen_8` (`nomor_dosen_8`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_1` FOREIGN KEY (`nomor_mahasiswa`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_10` FOREIGN KEY (`nomor_dosen_6`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_11` FOREIGN KEY (`nomor_dosen_7`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_12` FOREIGN KEY (`nomor_dosen_8`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_2` FOREIGN KEY (`nomor_dosen_wali`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_3` FOREIGN KEY (`nomor_kepala_prodi`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_4` FOREIGN KEY (`nomor_ketua_jurusan`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_5` FOREIGN KEY (`nomor_dosen_1`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_6` FOREIGN KEY (`nomor_dosen_2`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_7` FOREIGN KEY (`nomor_dosen_3`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_8` FOREIGN KEY (`nomor_dosen_4`) REFERENCES `tbl_user` (`nomor_induk`),
  CONSTRAINT `tbl_peserta_assesmen_ibfk_9` FOREIGN KEY (`nomor_dosen_5`) REFERENCES `tbl_user` (`nomor_induk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_peserta_assesmen`
--

LOCK TABLES `tbl_peserta_assesmen` WRITE;
/*!40000 ALTER TABLE `tbl_peserta_assesmen` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_peserta_assesmen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_prodi_if`
--

DROP TABLE IF EXISTS `tbl_prodi_if`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_prodi_if` (
  `kode_prodi` varchar(5) NOT NULL,
  `nama_prodi` varchar(100) NOT NULL,
  `jenjang` varchar(5) NOT NULL,
  PRIMARY KEY (`kode_prodi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_prodi_if`
--

LOCK TABLES `tbl_prodi_if` WRITE;
/*!40000 ALTER TABLE `tbl_prodi_if` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_prodi_if` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_register_approval`
--

DROP TABLE IF EXISTS `tbl_register_approval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_register_approval` (
  `nomor_induk` varchar(30) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `alamat` text NOT NULL,
  `email` varchar(100) NOT NULL,
  `telp` varchar(20) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` text NOT NULL,
  `approval_status` enum('Waiting','Accepted') NOT NULL DEFAULT 'Waiting',
  PRIMARY KEY (`nomor_induk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_register_approval`
--

LOCK TABLES `tbl_register_approval` WRITE;
/*!40000 ALTER TABLE `tbl_register_approval` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_register_approval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_user`
--

DROP TABLE IF EXISTS `tbl_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_user` (
  `nomor_induk` varchar(30) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `alamat` text NOT NULL,
  `email` varchar(100) NOT NULL,
  `telp` varchar(20) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` text NOT NULL,
  `role` enum('Admin','Dosen','Kepala Prodi','Sekretaris Jurusan','Ketua Jurusan') NOT NULL,
  PRIMARY KEY (`nomor_induk`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_user`
--

LOCK TABLES `tbl_user` WRITE;
/*!40000 ALTER TABLE `tbl_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-07-19 16:38:53
