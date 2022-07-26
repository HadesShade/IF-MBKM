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
  `status_berkas` enum('Belum Dikumpulkan','Dikumpulkan') NOT NULL DEFAULT 'Belum Dikumpulkan',
  PRIMARY KEY (`id_pengajuan`),
  CONSTRAINT `tbl_berkas_mbkm_ibfk_1` FOREIGN KEY (`id_pengajuan`) REFERENCES `tbl_pengajuan_mbkm` (`id_pengajuan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_berkas_mbkm`
--

LOCK TABLES `tbl_berkas_mbkm` WRITE;
/*!40000 ALTER TABLE `tbl_berkas_mbkm` DISABLE KEYS */;
INSERT INTO `tbl_berkas_mbkm` VALUES ('1111-25072022','http://127.0.0.1:5000/uploads/1111-25072022-sertifikatMBKM.pdf','http://127.0.0.1:5000/uploads/1111-25072022-laporanMBKM.pdf','http://127.0.0.1:5000/uploads/1111-25072022-hasilMBKM.pdf','2022-07-25','2022-07-28','http://127.0.0.1:5000/uploads/1111-25072022-dokumentasiMBKM.pdf','Dikumpulkan');
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
INSERT INTO `tbl_form_assesmen` VALUES ('1111-25072022-25072022','B+','A',NULL,NULL,NULL,NULL,NULL,NULL);
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
  UNIQUE KEY `id_pengajuan` (`id_pengajuan`),
  CONSTRAINT `tbl_kegiatan_assesmen_ibfk_1` FOREIGN KEY (`id_pengajuan`) REFERENCES `tbl_pengajuan_mbkm` (`id_pengajuan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kegiatan_assesmen`
--

LOCK TABLES `tbl_kegiatan_assesmen` WRITE;
/*!40000 ALTER TABLE `tbl_kegiatan_assesmen` DISABLE KEYS */;
INSERT INTO `tbl_kegiatan_assesmen` VALUES ('1111-25072022-25072022','1111-25072022','2022-07-25 21:46:00','Gedung Utama Ruang 7.5','Selesai');
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
INSERT INTO `tbl_mata_kuliah` VALUES ('IF101','Mata Kuliah 1',1),('IF102','Mata Kuliah 2',2),('IF103','Mata Kuliah 3',3),('IF104','Mata Kuliah 4',4),('IF105','Mata Kuliah 5',5),('IF106','Mata Kuliah 6',6),('IF107','Mata Kuliah 7',7),('IF108','Mata Kuliah 8',8);
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
INSERT INTO `tbl_matkul_mbkm` VALUES ('1111-25072022','IF102','1010','IF104','1212',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
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
INSERT INTO `tbl_pengajuan_mbkm` VALUES ('1111-25072022','1111','IF',2019,'LO KMIPN IV','Kepanitiaan','Politeknik Negeri Batam','http://127.0.0.1:5000/uploads/1111-25072022-buktiMBKM.pdf',6,'Accepted');
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
INSERT INTO `tbl_peserta_assesmen` VALUES ('1111-25072022-25072022','1111','7777','3333','2222','1010','1212',NULL,NULL,NULL,NULL,NULL,NULL);
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
INSERT INTO `tbl_prodi_if` VALUES ('AN','Teknik Animasi','D4'),('GM','Teknik Geomatika','D3'),('IF','Teknik Informatika','D3'),('MJ','Teknik Multimedia dan Jaringan','D4'),('RKS','Teknik Rekayasa Keamanan Siber','D4'),('TRPL','Teknik Rekayasa Perangkat Lunak','D4');
/*!40000 ALTER TABLE `tbl_prodi_if` ENABLE KEYS */;
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
  `role` enum('Mahasiswa','Dosen','Kepala Prodi','Sekretaris Jurusan','Ketua Jurusan') NOT NULL,
  PRIMARY KEY (`nomor_induk`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_user`
--

LOCK TABLES `tbl_user` WRITE;
/*!40000 ALTER TABLE `tbl_user` DISABLE KEYS */;
INSERT INTO `tbl_user` VALUES ('1010','dosen7','Batam','dosen7@polibatam.ac.id','081234567810','dosen7.1010','a543e8fcda2f0b318826667effe4e4b3ac22705112f9470d7e3d07c71ca1025d235e6d361160b5b2b0b61f7121b84234dd0ddbd00d206f8f4805fef04f595193','Dosen'),('1111','mhs','Batam','mhs@polibatam.ac.id','081234567890','mhs.1111','33275a8aa48ea918bd53a9181aa975f15ab0d0645398f5918a006d08675c1cb27d5c645dbd084eee56e675e25ba4019f2ecea37ca9e2995b49fcb12c096a032e','Mahasiswa'),('1212','dosen8','Batam','dosen8@polibatam.ac.id','081234567811','dosen8.1212','72cd06bd36df7019dbe93283eddc1774d205d2a52e247000683d69d9f47c56ac65fa5538404829518342c75d7f3175936df906fdafd3e5089c4c1e2f698b4a5a','Dosen'),('1313','sekjur','Batam','sekjur@polibatam.ac.id','081234567812','sekjur.1313','686e60e98df97d4cf1c34044d1573b0b40d111b80210e1afd1e3e51e6d62485cb2dcaf03b266579a78c1b5e4edc20457479f9152d75ff7efdb52ec54868ad123','Sekretaris Jurusan'),('2222','kajur','Batam','kajur@polibatam.ac.id','081234567891','kajur.2222','a8cebf1698dc14282c507b1e1cfb7f2c9d5216aa7bd0854b50561e02c2b99d9a38945ec0f81e55f9699062b1eac6d0083411c839ba2b27c6a15b494463bc5c73','Ketua Jurusan'),('3333','kaprodi','Batam','kaprodi@polibatam.ac.id','081234567893','kaprodi.3333','2f116a908cf26341547be5d4eec5d9e325fa75f1b6bfd6ba1618d9283b9aeb60cfb00a6a8508e0bcff4e673a52abf31cad6d7b26ba3994c087a0566ead3b2330','Kepala Prodi'),('4444','dosen1','Batam','dosen1@polibatam.ac.id','081234567894','dosen1.4444','c3e47544d233ab0c129605b325a5edfd8ad0a2b58e2ea910ffef872876139407c578d06ff4b9400332d0c438f5dcba9ff5ecbca372167322c73da291c1cef670','Dosen'),('5151','mhs2','Batam','mhs2@polibatam.ac.id','085555555555','mhs2.5151','c4a36a1b84dc99b13cc12bf2e371c7a92bde87354d55f830cd5e82db25d7598ba06a6532920476f951ce30197884f6a40fb07acba1e05ab541f8023c9c0f0072','Mahasiswa'),('5555','dosen2','Batam','dosen2@polibatam.ac.id','081234567895','dosen2.5555','b1db8b683bf3be35360e35d80db84b139d87aa3ffc21ac9ddb60af95fe0c694a30a3ae6b2468c94c3223c13fda8f8b45e2085cde506c51569af3257f5657bc27','Dosen'),('6666','dosen3','Batam','dosen3@polibatam.ac.id','081234567896','dosen3.6666','0549ab26aefcba2df2f37dc4a2820597b0142f86ac8984214951c44621b63d1696f03cc3093ba1c7c88a7259d5cc83e7396e1614d1a5f3c3c0ad96e70cdfd0d7','Dosen'),('7777','dosen4','Batam','dosen4@polibatam.ac.id','081234567897','dosen4.7777','498ad5123733c1e8fdc55bae5febc47aca3ea726c9408f4987db5c5b196258bc573c76498fbd5be09a137062f92ea2423f69a3aaaf5ffd3b80b1e96df4f96d17','Dosen'),('8888','dosen5','Batam','dosen5@polibatam.ac.id','081234567898','dosen5.8888','3e720266b7b7d8084466a12ec088fbfe1a5361a35619cd73603c1f935b153eebd7233249e1b50be05d56b95a78fafacbf8fb45b9b8d6d144932ab00754073486','Dosen'),('9999','dosen6','Batam','dosen6@polibatam.ac.id','081234567899','dosen6.9999','3e720266b7b7d8084466a12ec088fbfe1a5361a35619cd73603c1f935b153eebd7233249e1b50be05d56b95a78fafacbf8fb45b9b8d6d144932ab00754073486','Dosen');
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

-- Dump completed on 2022-07-26 12:22:21
