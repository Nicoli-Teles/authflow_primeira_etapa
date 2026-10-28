import { AuthService } from "./services/authService.js";
import { AuthValidator } from "./validators/authValidator.js";
import { AuthView } from "./ui/authView.js";
import { AuthController } from "./controllers/authController.js";

const authService = new AuthService();
const authValidator = new AuthValidator();
const authView = new AuthView();

const authController = new AuthController(
    authService,
    authValidator,
    authView
);

authController.init();