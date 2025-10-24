import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, CheckCircle2, XCircle, Link2, FileText, Search, Table } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [formData, setFormData] = useState({
    site_url: "",
    login: "",
    password: ""
  });
  const [navigating, setNavigating] = useState(false);
  const [adminUrl, setAdminUrl] = useState(null);
  const [formats, setFormats] = useState([]);
  const [selectedFormat, setSelectedFormat] = useState(null);
  const [showFormats, setShowFormats] = useState(false);
  const [tableData, setTableData] = useState(null);
  const [showFormatChoice, setShowFormatChoice] = useState(false);
  const [fileFormat, setFileFormat] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value} = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const startApp = async () => {
    if (!formData.site_url || !formData.login || !formData.password) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }

    setNavigating(true);
    setAdminUrl(null);
    setFormats([]);
    setShowFormats(false);

    try {
      const response = await axios.post(`${API}/connection/extract-formats`, formData);
      
      if (response.data.success) {
        toast.success(`${response.data.total_count} formats d'import récupérés !`);
        setFormats(response.data.formats);
        setShowFormats(true);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      console.error("Error extracting formats:", error);
      toast.error("Erreur lors de l'extraction des formats");
    } finally {
      setNavigating(false);
    }
  };

  const handleSelectFormat = (format) => {
    setSelectedFormat(format);
    toast.success(`Format sélectionné: ${format.name}`);
  };

  const continueWithFormat = async () => {
    if (!selectedFormat) {
      toast.error("Veuillez sélectionner un format");
      return;
    }

    setNavigating(true);
    setTableData(null);
    setShowFormatChoice(false);

    try {
      const response = await axios.post(`${API}/connection/extract-table`, {
        site_url: formData.site_url,
        login: formData.login,
        password: formData.password,
        selected_format: selectedFormat
      });

      if (response.data.success) {
        toast.success(`Configuration récupérée: ${response.data.total_rows} lignes !`);
        setTableData(response.data);
        setShowFormatChoice(true);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      console.error("Error extracting table:", error);
      toast.error("Erreur lors de l'extraction du tableau");
    } finally {
      setNavigating(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      toast.success(`Fichier sélectionné: ${file.name}`);
    }
  };

  const submitImport = async () => {
    if (!uploadedFile) {
      toast.error("Veuillez sélectionner un fichier");
      return;
    }

    if (!fileFormat) {
      toast.error("Veuillez choisir un format");
      return;
    }

    setUploading(true);

    try {
      const formDataUpload = new FormData();
      formDataUpload.append('file', uploadedFile);
      formDataUpload.append('file_format', fileFormat);
      formDataUpload.append('site_url', formData.site_url);
      formDataUpload.append('login', formData.login);
      formDataUpload.append('password', formData.password);
      formDataUpload.append('selected_format', JSON.stringify(selectedFormat));
      formDataUpload.append('table_config', JSON.stringify(tableData));

      const response = await axios.post(`${API}/import/execute`, formDataUpload, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        toast.success(response.data.message);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      console.error("Error importing:", error);
      toast.error("Erreur lors de l'import");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen" data-testid="home-page">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b backdrop-blur-sm bg-white/70 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg">
              <Link2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AutoImport by VPWhite</h1>
              <p className="text-sm text-gray-500">Automatisez vos imports Legisway</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-2xl mx-auto space-y-8">
          {/* Connection Form Card */}
          <Card className="border-0 shadow-xl" data-testid="connection-form">
            <CardHeader className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-t-lg">
              <CardTitle className="text-2xl text-gray-900">Configuration de connexion</CardTitle>
              <CardDescription className="text-gray-600">
                Entrez les informations pour vous connecter au site cible
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              <div className="space-y-2">
                <Label htmlFor="site_url" className="text-gray-700 font-medium">URL du site</Label>
                <Input
                  id="site_url"
                  name="site_url"
                  type="url"
                  placeholder="https://example.com/ng/login/"
                  value={formData.site_url}
                  onChange={handleInputChange}
                  className="h-11"
                  data-testid="site-url-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="login" className="text-gray-700 font-medium">Identifiant</Label>
                <Input
                  id="login"
                  name="login"
                  type="text"
                  placeholder="Votre identifiant"
                  value={formData.login}
                  onChange={handleInputChange}
                  className="h-11"
                  data-testid="login-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">Mot de passe</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Votre mot de passe"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="h-11"
                  data-testid="password-input"
                />
              </div>

              {adminUrl && (
                <Alert className="bg-blue-50 border-blue-200" data-testid="admin-url-result">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-blue-600" />
                    <AlertDescription className="text-blue-700">
                      Page d'administration atteinte ! URL: {adminUrl}
                    </AlertDescription>
                  </div>
                </Alert>
              )}

              <div className="pt-4">
                <Button
                  onClick={startApp}
                  disabled={navigating}
                  className="w-full h-12 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-600 hover:via-teal-600 hover:to-cyan-600 text-white font-bold text-lg shadow-lg hover:shadow-xl transition-all"
                  data-testid="start-app-button"
                >
                  {navigating ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      En cours...
                    </>
                  ) : (
                    "Start the app!"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Formats List */}
          {showFormats && formats.length > 0 && (
            <Card className="border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-t-lg">
                <CardTitle className="text-2xl text-gray-900 flex items-center gap-2">
                  <FileText className="w-6 h-6 text-blue-600" />
                  Formats d'import disponibles ({formats.length})
                </CardTitle>
                <CardDescription className="text-gray-600">
                  Sélectionnez un format pour continuer
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="mb-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      type="text"
                      placeholder="Rechercher un format..."
                      className="pl-10 h-11"
                      data-testid="search-format-input"
                    />
                  </div>
                </div>
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {formats.map((format, index) => (
                    <div
                      key={index}
                      onClick={() => handleSelectFormat(format)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        selectedFormat?.name === format.name
                          ? 'border-emerald-500 bg-emerald-50'
                          : 'border-gray-200 hover:border-emerald-300 hover:bg-gray-50'
                      }`}
                      data-testid={`format-item-${index}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${
                            selectedFormat?.name === format.name ? 'bg-emerald-500' : 'bg-gray-300'
                          }`} />
                          <span className="font-medium text-gray-900">{format.name}</span>
                        </div>
                        {selectedFormat?.name === format.name && (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                {selectedFormat && (
                  <div className="mt-6 pt-4 border-t space-y-4">
                    <Alert className="bg-emerald-50 border-emerald-200">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                      <AlertDescription className="text-emerald-700">
                        Format sélectionné : <strong>{selectedFormat.name}</strong>
                      </AlertDescription>
                    </Alert>
                    <Button
                      onClick={continueWithFormat}
                      disabled={navigating}
                      className="w-full h-12 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 text-white font-bold text-lg shadow-lg hover:shadow-xl transition-all"
                      data-testid="continue-format-button"
                    >
                      {navigating ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          Sélection en cours...
                        </>
                      ) : (
                        "Continuer avec ce format"
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Table Display */}
          {showTable && tableData && (
            <Card className="border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-t-lg">
                <CardTitle className="text-2xl text-gray-900 flex items-center gap-2">
                  <Table className="w-6 h-6 text-purple-600" />
                  Configuration du format ({tableData.total_rows} lignes)
                </CardTitle>
                <CardDescription className="text-gray-600">
                  Tableau de configuration extrait de {selectedFormat?.name}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-gray-100">
                        {tableData.headers.map((header, index) => (
                          <th
                            key={index}
                            className="border border-gray-300 px-3 py-2 text-left text-sm font-semibold text-gray-700"
                          >
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {tableData.rows.map((row, rowIndex) => (
                        <tr
                          key={rowIndex}
                          className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                        >
                          {row.cells.map((cell, cellIndex) => (
                            <td
                              key={cellIndex}
                              className="border border-gray-300 px-3 py-2 text-sm text-gray-800"
                            >
                              {cell || '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info Card */}
          <Card className="border-l-4 border-l-teal-400 bg-gradient-to-br from-slate-50 to-gray-50 shadow-md">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-lg">💡</span>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold text-gray-900">Comment ça marche ?</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>1. Entrez l'URL de connexion du site cible</li>
                    <li>2. Saisissez vos identifiants de connexion</li>
                    <li>3. Cliquez sur "Start the app!" pour extraire les formats</li>
                    <li>4. Sélectionnez le format souhaité dans la liste</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;